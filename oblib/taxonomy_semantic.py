# Copyright 2018 SunSpec Alliance

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Semantic taxonomy classes."""

import os
import xml.sax
from oblib import constants, taxonomy, util


class _ElementsHandler(xml.sax.ContentHandler):
    """
    Reads the files in solar-taxonomy/core/*.xsd .

    This extracts the metadata for each concept name, such as the datatype
    of the concept, whether it's nillable, etc.
    As a SAX parser, it streams the XML, and startElement() is called
    once for each element in the file.
    """

    def __init__(self):
        self._elements = {}

    def startElement(self, name, attrs):
        if name == "xs:element":

            # Temporary fix for the circular dependency issue
            from oblib import taxonomy
            
            element = taxonomy.ConceptDetails()
            
            for item in attrs.items():
                if item[0] == "abstract":
                    element.abstract = util.convert_taxonomy_xsd_bool(item[1])
                elif item[0] == "id":
                    # Turn the first underscore (only the first) into
                    # a colon. For example, the concept named
                    # solar:InverterPowerLevel10PercentMember_1 appears
                    # in the id field as
                    # solar_InverterPowerLevel10PercentMember_1. We want
                    # to replace the first underscore but not the second.
                    element.id = item[1].replace("_", ":", 1)
                elif item[0] == "name":
                    element.name = item[1]
                elif item[0] == "nillable":
                    element.nillable = util.convert_taxonomy_xsd_bool(item[1])
                elif item[0] == "solar:periodIndependent":
                    element.period_independent = util.convert_taxonomy_xsd_bool(item[1])
                elif item[0] == "substitutionGroup":
                    element.substitution_group = taxonomy.SubstitutionGroup(item[1])
                elif item[0] == "type":
                    element.type_name = item[1]
                elif item[0] == "xbrli:periodType":
                    # element.period_type = item[1]
                    element.period_type = taxonomy.PeriodType(item[1])
                elif item[0] == "xbrldt:typedDomainRef":
                    element.typed_domain_ref = item[1]
            self._elements[element.id] = element

    def elements(self):
        return self._elements


class _TaxonomySemanticHandler(xml.sax.ContentHandler):
    """
    Reads the files in solar-taxonomy/documents/<document name>/*_pre.xml .

    This extracts the list of concept names from the presentation file.
    As a SAX parser,it streams the XML, and startElement() is called
    once for each XML element in the file.
    """

    def __init__(self):
        self._concepts = []

    def startElement(self, name, attrs):
        if name == "loc":
            for item in attrs.items():
                if item[0] == "xlink:label":
                    concept = item[1].replace("_", ":", 1)
                    self._concepts.append(concept)

    def concepts(self):
        return self._concepts


class _TaxonomyRelationshipHandler(xml.sax.ContentHandler):
    """
    Reads the files in solar-taxonomy/documents/<document name>/*_def.xml .

    This extracts the relationships between the concepts, such as when one
    concept is a parent of another, when a concept belongs to a hypercube,
    etc.
    As a SAX parser,it streams the XML, and startElement() is called
    once for each XML element in the file.
    """

    def __init__(self):
        self._relationships = []

    def startElement(self, name, attrs):
        if name == "definitionArc":
            relationship = taxonomy.Relationship()
            for item in attrs.items():
                if item[0] == "xlink:arcrole":
                    relationship.role = taxonomy.RelationshipRole(item[1].split("/")[-1])
                if item[0] == "xlink:from":
                    relationship.from_ = item[1].replace("_", ":", 1)
                if item[0] == "xlink:to":
                    relationship.to = item[1].replace("_", ":", 1)
                if item[0] == "order":
                    relationship.order = item[1]
            self._relationships.append(relationship)
            # Question TBD: do we need to remember which document definition
            # this relationship came from? would the same concepts ever have
            # different relationships in one document than another?

    def relationships(self):
        return self._relationships


class TaxonomySemantic(object):
    """
    Manage semantic portions of the taxonomy including entrypoints, concepts,
    concepts_details, and relationships.
    """

    # Taxonomy data is internally held in three data structures:
    #    - _concept_Details is a map containing all concept details with their id as the key.  This maps to elements
    #      internal to the taxonomy XSD file abd the code that loads this structure uses the term elements to match
    #      the input data.
    #    - _concepts_by_entrypoint is a map containing all concepts for individual entrypoints.  The entrypoint is
    #      the key and the value is a list of all concepts in the entrypoint.
    #    - _relationships_by_entrypoint is a map containing all relationshsips for individual entrypoints.  The
    #      entrypoint is the key and the value is a list of all concepts in the entyrpoint.

    def __init__(self):
        """Constructor."""

        self._concepts_details = self._load_elements()
        self._concepts_by_entrypoint = self._load_concepts()
        self._relationships_by_entrypoint = self._load_relationships()
        self._reduce_unused_semantic_data()

    def _load_elements_file(self, pathname):
        eh = _ElementsHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(eh)
        parser.parse(open(pathname))
        return eh.elements()

    def _load_elements(self):
        elements = self._load_elements_file(os.path.join(
            constants.SOLAR_TAXONOMY_DIR, "core",
            "solar_2019-02-27_r01.xsd"))
        elements.update(self._load_elements_file(os.path.join(
            constants.SOLAR_TAXONOMY_DIR, "external",
            "us-gaap-2017-01-31.xsd")))
        elements.update(self._load_elements_file(os.path.join(
            constants.SOLAR_TAXONOMY_DIR, "external",
            "dei-2018-01-31.xsd")))
        return elements

    def _load_concepts_file(self, pathname):
        taxonomy = _TaxonomySemanticHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(taxonomy)
        parser.parse(open(pathname))
        return taxonomy.concepts()

    def _load_concepts(self):
        """Return a dict of available concepts."""

        concepts = {}

        for filename in os.listdir(
                os.path.join(constants.SOLAR_TAXONOMY_DIR, "data")):
            # if 'def.' in filename:
            if 'pre.' in filename:
                concept_name = filename[filename.find("solar-")+6:filename.find("_2019")]
                if concept_name == "cutsheet":   # Note: CutSheet is not named using camel case like other files
                    concept_name = "CutSheet"
                concepts[concept_name] = self._load_concepts_file(
                    os.path.join(constants.SOLAR_TAXONOMY_DIR,
                                 "data", filename))
        for filename in os.listdir(
                os.path.join(constants.SOLAR_TAXONOMY_DIR, "documents")):
            # if 'def.' in filename:
            if 'pre.' in filename:
                concept_name = filename[filename.find("solar-")+6:filename.find("_2019")]
                if concept_name == "cutsheet":   # Note: CutSheet is not named using camel case like other files
                    concept_name = "CutSheet"
                concepts[concept_name] = self._load_concepts_file(
                    os.path.join(constants.SOLAR_TAXONOMY_DIR,
                                 "documents", filename))

        for filename in os.listdir(
                os.path.join(constants.SOLAR_TAXONOMY_DIR, "process")):
            # if 'def.' in filename:
            if 'pre.' in filename:
                concept_name = filename[filename.find("solar-")+6:filename.find("_2019")]
                if concept_name == "cutsheet":   # Note: CutSheet is not named using camel case like other files
                    concept_name = "CutSheet"
                concepts[concept_name] = self._load_concepts_file(
                    os.path.join(constants.SOLAR_TAXONOMY_DIR,
                                 "process", filename))

        # load from "/core/" for the "All" entrypoint:
        concepts["All"] = self._load_concepts_file(
            os.path.join(constants.SOLAR_TAXONOMY_DIR, "core",
                             "solar_all_2019-02-27_r01_pre.xml"))
        return concepts

    def _load_relationships_file(self, fn):
        taxonomy = _TaxonomyRelationshipHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(taxonomy)
        parser.parse(open(os.path.join(constants.SOLAR_TAXONOMY_DIR, fn)))
        return taxonomy.relationships()

    def _load_relationships(self):
        relationships = {}
        for filename in os.listdir(os.path.join(constants.SOLAR_TAXONOMY_DIR, "data")):
            if 'def.' in filename:
                concept_name = filename[filename.find("solar-")+6:filename.find("_2019")]
                if concept_name == "cutsheet":   # Note: CutSheet is not named using camel case like other files
                    concept_name = "CutSheet"
                relationships[concept_name] = self._load_relationships_file(os.path.join("data", filename))

        for filename in os.listdir(os.path.join(constants.SOLAR_TAXONOMY_DIR, "documents")):
            if 'def.' in filename:
                concept_name = filename[filename.find("solar-")+6:filename.find("_2019")]
                if concept_name == "cutsheet":   # Note: CutSheet is not named using camel case like other files
                    concept_name = "CutSheet"
                relationships[concept_name] = self._load_relationships_file(os.path.join("documents", filename))

        for filename in os.listdir(os.path.join(constants.SOLAR_TAXONOMY_DIR, "process")):
            if 'def.' in filename:
                concept_name = filename[filename.find("solar-") + 6:filename.find("_2019")]
                if concept_name == "cutsheet":   # Note: CutSheet is not named using camel case like other files
                    concept_name = "CutSheet"
                relationships[concept_name] = self._load_relationships_file(os.path.join("process", filename))

        # load from "/core/" for the "All" entrypoint:
        relationships["All"] = self._load_relationships_file(
            os.path.join(constants.SOLAR_TAXONOMY_DIR, "core",
                         "solar_all_2019-02-27_r01_def.xml"))

        return relationships

    def _reduce_unused_semantic_data(self):
        """
        During loading of the elements unused elements may be loaded in the
        us-gaap and dei namespaces.  A new elements list can be created that
        does not contain them.  Although there is no other known cases of
        unused memory if any are found they should be addressed.

        Removing the elements has two benefits:
            - Allows simplifcation of accessor methods which no longer have to filter unused data.
            - Reduces in-memory footprint of data
        """
        # Create a list of elements in use and set them all to False
        concept_details_in_use = {}
        for e in self._concepts_details:
            concept_details_in_use[e] = False

        # Find all elements loaded by the taxonomy in the concepts object and
        # set them to True
        for key in self._concepts_by_entrypoint:
            for c in self._concepts_by_entrypoint[key]:
                concept_details_in_use[c] = True

        # Create a new elements list and only add the elements that are in use.
        ne = {}
        for e in self._concepts_details:
            if concept_details_in_use[e]:
                ne[e] = self._concepts_details[e]
        self._concepts_details = ne

    def get_all_concepts(self, details=False):
        """
        Return all concepts in the taxonomy.
        
        Args:
            details : boolean, default False

        Returns:
            list of concept names if details=False
            dict of concept details if details=True
        """
        if not details:
            return list(self._concepts_by_entrypoint)
        else:
            return self._concepts_details

    def get_all_type_names(self):
        """
        Used to access all type names in elements of the taxonomy.

        Returns:
             list of type names (strings).
        """
        type_names = set() # use set to eliminate duplicates
        for e in self._concepts_details:
            type_names.add(self._concepts_details[e].type_name)
        return list(type_names)

    def is_concept(self, concept):
        """
        Validate if a concept is present in the Taxonomy.

        Args:
            concept (string): Concept id with the namespace required.

        Return:
            True if concept is present, False otherwise.
        """

        if concept in self._concepts_details:
            return True
        else:
            return False

    def is_entrypoint(self, entrypoint):
        """
        Validate if an entrypoint type is present in the Taxonomy.

        Args:
            entrypoint (string): Entrypoint name to check for presence.

        Return:
            True if the entrypoint is present, False otherwise.
        """
        if entrypoint in self._concepts_by_entrypoint:
            return True
        else:
            return False

    def get_entrypoint_concepts(self, entrypoint, details=False):
        """
        Return a list of all concepts in the entrypoint, with concept details 
        (optional).

        Args:
            entrypoint: str
                name of the entrypoint
            details: boolean, default False
                if True return details for each concept

        Returns:
            concepts: list
                elements of the list are concept names
            details: dict
                primary key is name from concepts, value is dict of concept
                details
        """
        concepts = []
        if entrypoint in self._concepts_by_entrypoint:
            concepts = self._concepts_by_entrypoint[entrypoint]
            if details:
                ci = {}
                for concept in concepts:
                    if concept in self._concepts_details:
                        ci[concept] = self._concepts_details[concept]
                    else:
                        # NOTE: This is encountered if a historical bug in the Taxonomy occurs.
                        # Printing a warning will be left in case this reoccurs in the future.
                        print("Warning, concept not found:", concept)

                return concepts, ci
        return concepts

    def get_entrypoint_relationships(self, entrypoint):
        """
        Used to find the relationships for an entrypoint.

        Args:
            Entrypoint (string): Entrypoint name to lookup relationships for.

        Returns:
             A list of all relationships in an entry point.  Iif the concept exists but has no
             relationships an empty list is returned.
        """

        if entrypoint in self._concepts_by_entrypoint:
            if entrypoint in self._relationships_by_entrypoint:
                return self._relationships_by_entrypoint[entrypoint]
            else:
                return []
        else:
            return None

    def get_all_entrypoints(self):
        """
        Used to access  a list of all entry points (data, documents, and processes) in the Taxonomy.

        Returns:
            A list of entrypoint names (strings).
        """
    
        return list(self._concepts_by_entrypoint)

    def get_concept_details(self, concept):
        """
        Return information on a single concept.

        Args:
            concept : str
                concept name

        Returns:
            dict containing concept attributes

        Raises:
            KeyError if concept is not found
        """
        if self.is_concept(concept):
            return self._concepts_details[concept]
        else:
            raise KeyError('{} is not a concept in the taxonomy'.format(concept))
            return None
