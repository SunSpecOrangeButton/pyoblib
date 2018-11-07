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

import unittest
import taxonomy_units

tax = taxonomy_units.TaxonomyUnits()


class TestTaxonomyUnits(unittest.TestCase):

    def test_taxonomy_units(self):
        self.assertEqual(len(tax.units()), 296)

    def test_validate_unit(self):
        self.assertTrue(tax.validate_unit("acre"))
        self.assertTrue(tax.validate_unit("oz"))
        self.assertTrue(tax.validate_unit("rad"))
        self.assertFalse(tax.validate_unit("acrre"))
        self.assertFalse(tax.validate_unit("ozz"))
        self.assertFalse(tax.validate_unit("rrad"))

    def test_unit(self):
        unit = tax.unit("VAh")
        self.assertEqual(unit.id, "u00291")
        self.assertEqual(unit.unit_id, "VAh")
        self.assertEqual(unit.unit_name, "Volt-ampere-hours")
        self.assertEqual(unit.ns_unit, "http://www.xbrl.org/2009/utr")
        self.assertEqual(unit.item_type, "energyItemType")
        self.assertEqual(unit.item_type_date, "2009-12-16")
        self.assertEqual(unit.symbol, "VAh")
        self.assertEqual(unit.definition, "Volt-ampere (VA) hours of energy.")
        self.assertEqual(unit.base_standard, "Customary")
        self.assertEqual(unit.status, "CR")
        self.assertEqual(unit.version_date, "2017-07-12")
