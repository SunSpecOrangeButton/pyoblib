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

"""Taxonomy types."""

import os
import xml.sax
from oblib import constants


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


class TaxonomyTypes(object):
    """
    Represents Taxonomy Types.

    Allows lookup of enumerated values for each Taxonomy Type.

    Please note that in the implementation of this class the variable name
    "type" is never used although "_type" and "types" are in order to avoid
    confusion with the python "type" builtin.
    """

    def __init__(self):
        """Constructor."""
        self._types = self._load_types()

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

    def get_all_types(self):
        """
        Used to lookup all types.

        Returns:
             A map and sublists of types.
        """
        return self._types

    def is_type(self, name):
        """
        Validates that a type is in the taxonomy.

        Returns:
            True if the type is present, false otherwise.
        """
        if name in self._types:
            return True
        else:
            return False

    def get_type_enum(self, name):
        """
        Used to lookup a type enumeration.

        Returns:
             An enumeration given a type or None if the type does not exist
             in the taxonomy.
        """
        if name in self._types:
            return self._types[name]
        else:
            return None
