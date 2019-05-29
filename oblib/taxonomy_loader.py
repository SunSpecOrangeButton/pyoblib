# Copyright 2019 SunSpec Alliance

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Handles Loading of Orange Button Taxonomy.  No external functionality exposed."""

import xml.sax
import os
import sys

from oblib import constants, util, taxonomy


class _TaxonomyUnitsHandler(xml.sax.ContentHandler):
    """Loads Taxonomy Units from the units type registry file."""

    def __init__(self):
        self._units = {}

    def startElement(self, name, attrs):
        if name == "unit":
            for item in attrs.items():
                if item[0] == "id":

                    self._curr = taxonomy.Unit()
                    self._curr.id = item[1]
        elif name == "xs:enumeration":
            for item in attrs.items():
                if item[0] == "value":
                    self._curr.append(item[1])

    def characters(self, content):
        self._content = content

    def endElement(self, name):
        if name == "unitId":
            self._curr.unit_id = self._content
            self._units[self._content] = self._curr
        elif name == "unitName":
            self._curr.unit_name = self._content
        elif name == "nsUnit":
            self._curr.ns_unit = self._content
        elif name == "itemType":
            self._curr.item_type = self._content
        elif name == "itemTypeDate":
            self._curr.item_type_date = util.convert_taxonomy_xsd_date(self._content)
        elif name == "symbol":
            self._curr.symbol = self._content
        elif name == "definition":
            self._curr.definition = self._content
        elif name == "baseStandard":

            self._curr.base_standard = taxonomy.BaseStandard(self._content)
        elif name == "status":

            self._curr.status = taxonomy.UnitStatus(self._content)
        elif name == "versionDate":
            self._curr.version_date = util.convert_taxonomy_xsd_date(self._content)

    def units(self):
        return self._units


class _TaxonomyTypesHandler(xml.sax.ContentHandler):
    """Loads Taxonomy Types from the solar types xsd file."""

    def __init__(self):
        self._types = {}

    def startElement(self, name, attrs):
        if name == "complexType":
            for item in attrs.items():
                if item[0] == "name":
                    self._curr = []
                    if ":" in item[1]:
                        name = item[1]
                    else:
                        name = "solar-types:" + item[1]
                    self._types[name] = self._curr
        elif name == "xs:enumeration":
            for item in attrs.items():
                if item[0] == "value":
                    self._curr.append(item[1])

    def types(self):
        return self._types


class _TaxonomyNumericHandler(xml.sax.ContentHandler):
    """Loads Taxonomy Numeric Types from the numeric us xsd file."""

    def __init__(self):
        """Numeric handler constructor."""
        self._numeric_types = []

    def startElement(self, name, attrs):
        if name == "complexType":
            for item in attrs.items():
                if item[0] == "name":
                    if ":" in item[1]:
                        name = item[1]
                    else:
                        name = "num-us:" + item[1]
                    self._numeric_types.append(name)

    def numeric_types(self):
        return self._numeric_types


class _TaxonomyRefPartsHandler(xml.sax.ContentHandler):
    """Loads Taxonomy Ref Parts from the numeric us xsd file."""

    def __init__(self):
        """Ref parts constructor."""
        self._ref_parts = []

    def startElement(self, name, attrs):
        if name == "xs:element":
            for item in attrs.items():
                if item[0] == "name":
                    self._ref_parts.append(item[1])

    def ref_parts(self):
        return self._ref_parts


class _TaxonomyGenericRolesHandler(xml.sax.ContentHandler):
    """Loads Taxonomy Generic Roles from the generic roles xsd file."""

    def __init__(self):
        """Generic role handler constructor."""
        self._generic_roles = []
        self._process = False

    def startElement(self, name, attrs):
        if name == "link:definition":
            self._process = True

    def endElement(self, name):
        if name == "link:definition":
            self._process = False

    def characters(self, content):
        if self._process:
            self._generic_roles.append(content)

    def roles(self):
        return self._generic_roles


class _TaxonomyDocumentationHandler(xml.sax.ContentHandler):
    """Loads Taxonomy Docstrings from Labels file"""

    def __init__(self):
        """Ref parts constructor."""
        self._documentation = {}
        self._awaiting_text_for_concept = None

    def startElement(self, name, attrs):
        # Technically we should be using the labelArc element to connect a label
        # element to a loc element and the loc element refers to a concept by its anchor
        # within the main xsd, but that's really complicated and in practice the
        # xlink:label atrr in the <label> element seems to always be "label_" plus the
        # name of the concept.
        concept = None
        role = None
        if name == "label":
            for item in attrs.items():
                # Do we care about the difference between xlink:role="http:.../documentation"
                # and xlink:role="http:.../label" ??
                if item[0] == "xlink:label":
                    concept = item[1].replace("label_solar_", "solar:")
                if item[0] == "xlink:role":
                    role = item[1]
        if concept is not None and role == "http://www.xbrl.org/2003/role/documentation":
            self._awaiting_text_for_concept = concept

    def characters(self, chars):
        if self._awaiting_text_for_concept is not None:
            self._documentation[ self._awaiting_text_for_concept] = chars

    def endElement(self, name):
        self._awaiting_text_for_concept = None

    def docstrings(self):
        return self._documentation


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
                elif item[0] == "xbrldt:typedDomainRef":
                    element.typed_domain_ref = item[1]
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


class TaxonomyLoader(object):

    """
    Class for Taxonomy loading.

    Use this class to load the Taxonomy
    """

    def __init__(self):
        """Taxonomy Loader constructor."""
        pass


    def load(self):
        """"Load and return a Taxonomy."""
        pass

    def _load_numeric_types_file(self, pathname):
        tax = _TaxonomyNumericHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(tax)
        parser.parse(open(pathname))
        return tax.numeric_types()

    def _load_numeric_types(self):
        pathname = os.path.join(constants.SOLAR_TAXONOMY_DIR, "core")
        for filename in os.listdir(pathname):
            if 'numeric' in filename:
                numeric_types = self._load_numeric_types_file(os.path.join(
                    pathname, filename))
        return numeric_types

    def _load_generic_roles_file(self, pathname):
        tax = _TaxonomyGenericRolesHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(tax)
        parser.parse(open(pathname))
        return tax.roles()

    def _load_generic_roles(self):
        pathname = os.path.join(constants.SOLAR_TAXONOMY_DIR, "core")
        for filename in os.listdir(pathname):
            if 'gen-roles' in filename:
                generic_roles = self._load_generic_roles_file(os.path.join(
                    pathname, filename))
        return generic_roles

    def _load_ref_parts_file(self, pathname):
        tax = _TaxonomyRefPartsHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(tax)
        parser.parse(open(pathname))
        return tax.ref_parts()

    def _load_ref_parts(self):
        pathname = os.path.join(constants.SOLAR_TAXONOMY_DIR, "core")
        for filename in os.listdir(pathname):
            if 'ref-parts' in filename:
                ref_parts = self._load_ref_parts_file(os.path.join(pathname,
                                                                   filename))
        return ref_parts

    def _load_documentation(self):
        label_file = "solar_2019-02-27_r01_lab.xml"
        filename = os.path.join(constants.SOLAR_TAXONOMY_DIR, "core", label_file)

        taxonomy = _TaxonomyDocumentationHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(taxonomy)
        parser.parse(open(filename))
        return taxonomy._documentation

    def _load_types_file(self, pathname):
        taxonomy = _TaxonomyTypesHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(taxonomy)
        parser.parse(open(pathname))
        return taxonomy.types()

    def _load_types(self):
        pathname = os.path.join(constants.SOLAR_TAXONOMY_DIR, "core")
        for filename in os.listdir(pathname):
            if 'types' in filename:
                types = self._load_types_file(os.path.join(pathname, filename))
        return types

    def _load_units_file(self, fn):
        taxonomy = _TaxonomyUnitsHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(taxonomy)
        if sys.version_info[0] < 3:
            # python 2.x
            with open(fn, 'r') as infile:
                parser.parse(infile)
        else:
            with open(fn, 'r', encoding='utf8') as infile:
                parser.parse(infile)
        return taxonomy.units()

    def _load_units(self):
        pathname = os.path.join(constants.SOLAR_TAXONOMY_DIR, "external")
        filename = "utr.xml"
        units = self._load_units_file(os.path.join(pathname, filename))
        return units


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
                concept_name = filename[filename.find("solar-") + 6:filename.find("_2019")]
                if concept_name == "cutsheet":  # Note: CutSheet is not named using camel case like other files
                    concept_name = "CutSheet"
                concepts[concept_name] = self._load_concepts_file(
                    os.path.join(constants.SOLAR_TAXONOMY_DIR,
                                 "data", filename))
        for filename in os.listdir(
                os.path.join(constants.SOLAR_TAXONOMY_DIR, "documents")):
            # if 'def.' in filename:
            if 'pre.' in filename:
                concept_name = filename[filename.find("solar-") + 6:filename.find("_2019")]
                if concept_name == "cutsheet":  # Note: CutSheet is not named using camel case like other files
                    concept_name = "CutSheet"
                concepts[concept_name] = self._load_concepts_file(
                    os.path.join(constants.SOLAR_TAXONOMY_DIR,
                                 "documents", filename))

        for filename in os.listdir(
                os.path.join(constants.SOLAR_TAXONOMY_DIR, "process")):
            # if 'def.' in filename:
            if 'pre.' in filename:
                concept_name = filename[filename.find("solar-") + 6:filename.find("_2019")]
                if concept_name == "cutsheet":  # Note: CutSheet is not named using camel case like other files
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
                concept_name = filename[filename.find("solar-") + 6:filename.find("_2019")]
                if concept_name == "cutsheet":  # Note: CutSheet is not named using camel case like other files
                    concept_name = "CutSheet"
                relationships[concept_name] = self._load_relationships_file(os.path.join("data", filename))

        for filename in os.listdir(os.path.join(constants.SOLAR_TAXONOMY_DIR, "documents")):
            if 'def.' in filename:
                concept_name = filename[filename.find("solar-") + 6:filename.find("_2019")]
                if concept_name == "cutsheet":  # Note: CutSheet is not named using camel case like other files
                    concept_name = "CutSheet"
                relationships[concept_name] = self._load_relationships_file(os.path.join("documents", filename))

        for filename in os.listdir(os.path.join(constants.SOLAR_TAXONOMY_DIR, "process")):
            if 'def.' in filename:
                concept_name = filename[filename.find("solar-") + 6:filename.find("_2019")]
                if concept_name == "cutsheet":  # Note: CutSheet is not named using camel case like other files
                    concept_name = "CutSheet"
                relationships[concept_name] = self._load_relationships_file(os.path.join("process", filename))

        # load from "/core/" for the "All" entrypoint:
        relationships["All"] = self._load_relationships_file(
            os.path.join(constants.SOLAR_TAXONOMY_DIR, "core",
                         "solar_all_2019-02-27_r01_def.xml"))

        return relationships
