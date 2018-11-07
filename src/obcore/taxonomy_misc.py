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

import constants


#
# TODO: All taxonomy files are covered except for solar-ref-roles which has only one entry.
# It could be included for completeness.
#


class _TaxonomyNumericHandler(xml.sax.ContentHandler):
    """
    Loads Taxonomy Numeric Types from the numeric us xsd file.
    """

    def __init__(self):
        self._numeric_types = []

    def startElement(self, name, attrs):
        if name == "complexType":
            for item in attrs.items():
                if item[0] == "name":
                    self._numeric_types.append(item[1])

    def numeric_types(self):
        return self._numeric_types


class _TaxonomyRefPartsHandler(xml.sax.ContentHandler):
    """
    Loads Taxonomy Ref Parts from the numeric us xsd file.
    """

    def __init__(self):
        self._ref_parts = []

    def startElement(self, name, attrs):
        if name == "xs:element":
            for item in attrs.items():
                if item[0] == "name":
                    self._ref_parts.append(item[1])

    def ref_parts(self):
        return self._ref_parts


class _TaxonomyGenericRolesHandler(xml.sax.ContentHandler):
    """
    Loads Taxonomy Generic Roles from the generic roles xsd file.
    """

    def __init__(self):
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


class TaxonomyMisc(object):
    """
    Represents Miscellaneous Taxonomy Objects that are not covered in the
    other classes.  Generally speaking these are rarely used.
    """

    def __init__(self):
        self._numeric_types = self._load_numeric_types()
        self._generic_roles = self._load_generic_roles()
        self._ref_parts = self._load_ref_parts()

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
                ref_parts = self._load_ref_parts_file(os.path.name(pathname,
                                                                   filename))
        return ref_parts

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

    def numeric_types(self):
        """
        A list of numeric types.
        """

        return self._numeric_types

    def validate_numeric_type(self, numeric_type):
        """
        Check if a numeric type is valid.
        """

        if numeric_type in self._numeric_types:
            return True
        else:
            return False

    def ref_parts(self):
        """
        A list of ref parts.
        """

        return self._ref_parts

    def validate_ref_part(self, ref_part):
        """
        Check if a ref part is valid.
        """

        if ref_part in self._ref_parts:
            return True
        else:
            return False

    def generic_roles(self):
        """
        A list of generic roles
        """

        return self._generic_roles

    def validate_generic_role(self, generic_role):
        """
        Check if a generic role is valid.
        """

        if generic_role in self._generic_roles:
            return True
        else:
            return False
