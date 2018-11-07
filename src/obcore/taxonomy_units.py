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

import xml.sax

import taxonomy
import constants


class _TaxonomyUnitsHandler(xml.sax.ContentHandler):
    """
    Loads Taxonomy Units from the units type registry file.
    """

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
            self._curr.item_type_date = self._content
        elif name == "symbol":
            self._curr.symbol = self._content
        elif name == "definition":
            self._curr.definition = self._content
        elif name == "baseStandard":
            self._curr.base_standard = self._content
        elif name == "status":
            self._curr.status = self._content
        elif name == "versionDate":
            self._curr.version_date = self._content

    def units(self):
        return self._units


class TaxonomyUnits(object):
    """
    Represents Taxonomy Units and allows lookup of enumerated values for each Taxonomy Unit.
    """

    def __init__(self):
        self._units = self._load_units()

    def _load_units_file(self, fn):
        tax = _TaxonomyUnitsHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(tax)
        parser.parse(open(constants.SOLAR_TAXONOMY_DIR + fn))
        return tax.units()

    def _load_units(self):
        units = self._load_units_file("/external/utr.xml")
        return units

    def units(self):
        """
        Returns a map and sublists of all units.
        """

        return self._units

    def validate_unit(self, unit_id):
        """
        Validates that a unit is in the taxonomy based on its id.
        """

        if unit_id in self._units:
            return True
        else:
            return False

    def unit(self, unit_id):
        """
        Returns an unit given a unit_id or None if the type does not exist in the taxonomy.
        """

        if unit_id in self._units:
            return self._units[unit_id]
        else:
            return None
