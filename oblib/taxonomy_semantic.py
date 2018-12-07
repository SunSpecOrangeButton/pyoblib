"""Semantic taxonomy classes."""

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import xml.sax

import constants
import taxonomy
import util
import validator


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
            element = taxonomy.Element()
            for item in attrs.items():
                if item[0] == "abstract":
                    element.abstract = util.convert_taxonomy_bool(item[1])
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
                    element.nillable = util.convert_taxonomy_bool(item[1])
                elif item[0] == "solar:periodIndependent":
                    element.period_independent = util.convert_taxonomy_bool(item[1])
                elif item[0] == "substitutionGroup":
                    element.substitution_group = taxonomy.SubstitutionGroup(item[1])
                elif item[0] == "type":
                    element.type_name = item[1]
                elif item[0] == "xbrli:periodType":
                    element.period_type = taxonomy.PeriodType(item[1])
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
            relationship = {
                "role": None,
                "from": None,
                "to": None,
                "order": None
            }
            for item in attrs.items():
                if item[0] == "xlink:arcrole":
                    relationship['role'] = item[1].split("/")[-1]
                if item[0] == "xlink:from":
                    relationship['from'] = item[1].replace("_", ":", 1)
                if item[0] == "xlink:to":
                    relationship['to'] = item[1].replace("_", ":", 1)
                if item[0] == "order":
                    relationship['order'] = item[1]
            self._relationships.append(relationship)
            # Question TBD: do we need to remember which document definition
            # this relationship came from? would the same concepts ever have
            # different relationships in one document than another?

    def relationships(self):
        return self._relationships


class TaxonomySemantic(object):
    """Manage taxonomy elements and concepts."""

    def __init__(self):
        """Constructor."""
        self._elements = self._load_elements()
        self._concepts = self._load_concepts()
        self._relationships = self._load_relationships()
        self._reduce_memory_footprint()

    def _load_elements_file(self, pathname):
        eh = _ElementsHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(eh)
        parser.parse(open(pathname))
        return eh.elements()

    def _load_elements(self):
        elements = self._load_elements_file(os.path.join(
            constants.SOLAR_TAXONOMY_DIR, "core",
            "solar_2018-03-31_r01.xsd"))
        elements.update(self._load_elements_file(os.path.join(
            constants.SOLAR_TAXONOMY_DIR, "external",
            "us-gaap-2017-01-31.xsd")))
        elements.update(self._load_elements_file(os.path.join(
            constants.SOLAR_TAXONOMY_DIR, "external",
            "dei-2018-01-31.xsd")))
        return elements

    def _load_concepts_file(self, pathname):
        tax = _TaxonomySemanticHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(tax)
        parser.parse(open(pathname))
        return tax.concepts()

    def _load_concepts(self):
        """Return a dict of available concepts."""
        # TODO: Better understand the relationship of "def" vs. "pre" xml
        # files. Using pre seems to load a more accurate representation
        # of the taxonomy but this was found via trial and error as opposed
        # to a scientific methodology.
        concepts = {}
        for dirname in os.listdir(os.path.join(constants.SOLAR_TAXONOMY_DIR,
                                               "data")):
            for filename in os.listdir(
                    os.path.join(constants.SOLAR_TAXONOMY_DIR, "data",
                                 dirname)):
                # if 'def.' in filename:
                if 'pre.' in filename:
                    concepts[dirname] = self._load_concepts_file(
                        os.path.join(constants.SOLAR_TAXONOMY_DIR,
                                     "data", dirname, filename))
        for dirname in os.listdir(os.path.join(constants.SOLAR_TAXONOMY_DIR,
                                               "documents")):
            for filename in os.listdir(
                    os.path.join(constants.SOLAR_TAXONOMY_DIR, "documents",
                                 dirname)):
                # if 'def.' in filename:
                if 'pre.' in filename:
                    concepts[dirname] = self._load_concepts_file(
                        os.path.join(constants.SOLAR_TAXONOMY_DIR,
                                     "documents", dirname, filename))
        return concepts

    def _load_relationships_file(self, fn):
        tax = _TaxonomyRelationshipHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(tax)
        parser.parse(open(os.path.join(constants.SOLAR_TAXONOMY_DIR, fn)))
        return tax.relationships()

    def _load_relationships(self):
        relationships = {}
        for dirname in os.listdir(os.path.join(constants.SOLAR_TAXONOMY_DIR,
                                               "documents")):
            for filename in os.listdir(os.path.join(constants.SOLAR_TAXONOMY_DIR, "documents", dirname)):
                if 'def.' in filename:
                    relationships[dirname] = self._load_relationships_file(os.path.join("documents", dirname, filename))
        return relationships

    def _reduce_memory_footprint(self):
        """
        Reduce the memory footprint post load by removing unused data.

        During loading of the elements unused elements may be loaded in the
        us-gaap and dei namespaces.  A new elements list can be created that
        does not contain them.  Although there is no other known cases of
        unused memory if any are found they should be addressed.
        """
        # Create a list of elements in use and set them all to False
        elements_in_use = {}
        for e in self._elements:
            elements_in_use[e] = False

        # Find all elements loaded by the taxonomy in the concepts object and
        # set them to True
        for key in self._concepts:
            for c in self._concepts[key]:
                elements_in_use[c] = True

        # Create a new elements list and only add the elements that are in use.
        ne = {}
        for e in self._elements:
            if elements_in_use[e]:
                ne[e] = self._elements[e]
        self._elements = ne

    def elements(self):
        """Return a map of elements."""
        return self._elements

    def validate_concept(self, concept):
        """Validate if a concept is present in the Taxonomy."""
        found = False
        for c in self._concepts:
            for cc in self._concepts[c]:
                if cc == concept:
                    found = True
                    break
        return found

    def validate_concept_value(self, concept, value):
        """
        Validate a concept.

        Validates whether a concept is present in the Taxonomy and if
        its value is legal.
        """
        # Check presence
        found = False
        concept_info = False
        for c in self._concepts:
            for cc in self._concepts[c]:
                if cc == concept:
                    found = True
                    concept_info = self.concept_info(concept)
                    break
        if not found:
            return ["'{}' concept not found.".format(concept)]

        return validator.validate_concept_value(concept_info, value)

    def validate_ep(self, data):
        """Validate if an end point type is present in the Taxonomy."""
        if data in self._concepts:
            return True
        else:
            return False

    def concepts_ep(self, data):
        """Return a list of all concepts in an entry point."""
        if data in self._concepts:
            return self._concepts[data]
        else:
            return None

    def relationships_ep(self, entry_point):
        """
        Returns a list of all relationships in an entry point
        Returns an empty list if the concept exists but has no relationships
        """

        if entry_point in self._concepts:
            if entry_point in self._relationships:
                return self._relationships[entry_point]
            else:
                return []
        else:
            return None

    def entry_points(self):
        """
        Returns a list of all entry points (data, documents, and processes) in the Taxonomy.
        """
    
        return list(self._concepts)

    def concept_info(self, concept):
        """Return information on a single concept."""
        found = False
        for c in self._concepts:
            for cc in self._concepts[c]:
                if cc == concept:
                    found = True
                    break
        if not found:
            return None
        if concept in self._elements:
            return self._elements[concept]
        else:
            return None

    def concepts_info_ep(self, data):
        """
        Return concepts from an endpoints.

        Return a list of all concepts and their attributes in an end point.
        """
        if data in self._concepts:
            ci = []
            for concept in self._concepts[data]:
                if concept in self._elements:
                    ci.append(self._elements[concept])
                else:
<<<<<<< HEAD
                    # TODO: This is now known to be a bug in the taxonomy and has been submitted for fix.
=======
                    # TODO: This case is not correctly understood.
>>>>>>> 18972523822ab9dc3a33ab260766ff0b68efc16d
                    # Here are some samples that are not found:
                    # Warning, concept not found: solar:MeterRatingAccuracy_1
                    # Warning, concept not found: solar:MeterRevenueGrade_1
                    # Warning, concept not found: solar:MeterBidirectional_1
                    # Warning, concept not found: solar:RevenueMeterPowerFactor_1
                    # Warning, concept not found: solar:InverterPowerLevel10PercentMember_1
<<<<<<< HEAD
                    # This case should be understood and handled correctly as opposed to just printing a warning message.
=======
                    # This case should be understood and handled correctly as
                    # opposed to just printing a warning message.
>>>>>>> 18972523822ab9dc3a33ab260766ff0b68efc16d
                    # print("Warning, concept not found:", concept)
                    pass
            return ci
        else:
            return None
