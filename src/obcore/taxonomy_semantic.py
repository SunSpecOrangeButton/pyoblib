# Copyright 2018 Wells Fargo

# Licensed under the Apache License, Version 2.0 (the "License");
# pyou may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import xml.sax

import taxonomy
import validator


class _ElementsHandler(xml.sax.ContentHandler):

    def __init__(self):
        self._elements = {}

    def startElement(self, name, attrs):
        if name == "xs:element":
            element = taxonomy.Element()
            for item in attrs.items():
                if item[0] == "abstract":
                    if item[1] == "false":
                        element.abstact = False
                    else:
                        element.abstract = True
                elif item[0] == "id":
                    element.id = item[1].replace("_", ":")
                elif item[0] == "name":
                    element.name = item[1]
                elif item[0] == "nillable":
                    if item[1] == "false":
                        element.nillable = False
                    else:
                        element.nillable = True
                elif item[0] == "solar:periodIndependent":
                    element.period_independent = item[1]
                elif item[0] == "substitutionGroup":
                    element.substitution_group = item[1]
                elif item[0] == "type":
                    element.type_name = item[1]
                elif item[0] == "xbrli:periodType":
                    element.period_type = item[1]
            self._elements[element.id] = element

    def elements(self):
        return self._elements


class _TaxonomySemanticHandler(xml.sax.ContentHandler):

    def __init__(self):
        self._concepts = []

    def startElement(self, name, attrs):
        if name == "loc":
            for item in attrs.items():
                if item[0] == "xlink:label":
                    concept = item[1].replace("_", ":")
                    self._concepts.append(concept)

    def concepts(self):
        return self._concepts


class TaxonomySemantic(object):

    def __init__(self):
        self._elements = self._load_elements()
        self._concepts = self._load_concepts()

    def _load_elements_file(self, pathname):
        eh = _ElementsHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(eh)
        parser.parse(open(pathname))
        return eh.elements()

    def _load_elements(self):
        elements = self._load_elements_file(os.path.join(
                taxonomy.SOLAR_TAXONOMY_DIR, "core",
                "solar_2018-03-31_r01.xsd"))
        elements.update(self._load_elements_file(os.path.join(
                taxonomy.SOLAR_TAXONOMY_DIR, "external",
                "us-gaap-2017-01-31.xsd")))
        return elements

    def elements(self):
        """
        Returns a map of elements.
        """
        return self._elements

    def _load_concepts_file(self, pathname):
        tax = _TaxonomySemanticHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(tax)
        parser.parse(open(pathname))
        return tax.concepts()

    def _load_concepts(self):
        """
        Returns a dict of available concepts
        """
        # TODO: Better understand the relationship of "def" vs. "pre" xml files.  Using pre seems
        # to load a more accurate representation of the taxonomy but this was found via trial and
        # error as opposed to a scientific methodology.
        concepts = {}
        for dirname in os.listdir(os.path.join(taxonomy.SOLAR_TAXONOMY_DIR,
                                               "data")):
            for filename in os.listdir(
                    os.path.join(taxonomy.SOLAR_TAXONOMY_DIR, "data",
                                 dirname)):
                # if 'def.' in filename:
                if 'pre.' in filename:
                    concepts[dirname] = self._load_concepts_file(
                            os.path.join("data", dirname, filename))
        for dirname in os.listdir(os.path.join(taxonomy.SOLAR_TAXONOMY_DIR,
                                               "documents")):
            for filename in os.listdir(
                    os.path.join(taxonomy.SOLAR_TAXONOMY_DIR, "documents",
                                 dirname)):
                # if 'def.' in filename:
                if 'pre.' in filename:
                    concepts[dirname] = self._load_concepts_file(
                            os.path.join(taxonomy.SOLAR_TAXONOMY_DIR,
                                         "documents", dirname, filename))
        return concepts

    def validate_concept(self, concept):
        """
        Validates if a concept is present in the Taxonomy
        """

        found = False
        for c in self._concepts:
            for cc in self._concepts[c]:
                if cc == concept:
                    found = True
                    break
        return found

    def validate_concept_value(self, concept, value):
        """
        Validates if a concept is present in the Taxonomy and that its value is legal.
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
            return found

        return validator.validate_concept_value(concept_info, value)

    def validate_ep(self, data):
        """
        Validates if an end point type is present in the Taxonomy
        """

        if data in self._concepts:
            return True
        else:
            return False

    def concepts_ep(self, data):
        """
        Returns a list of all concepts in an end point
        """

        if data in self._concepts:
            return self._concepts[data]
        else:
            return None

    def concept_info(self, concept):
        """
        Returns information on a single concept.
        """

        found = False
        for c in self._concepts:
            for cc in self._concepts[c]:
                if cc == concept:
                    found = True
                    break
        if not found:
            return None
        return self._elements[concept]

    def concepts_info_ep(self, data):
        """
        Returns a list of all concepts and their attributes in an end point
        """

        if data in self._concepts:
            ci = []
            for concept in self._concepts[data]:
                ci.append(self._elements[concept])
            return ci
        else:
            return None
