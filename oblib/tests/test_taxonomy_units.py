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

import datetime
import unittest
from oblib import taxonomy, taxonomy_units


tax = taxonomy_units.TaxonomyUnits()


class TestTaxonomyUnits(unittest.TestCase):

    def test_is_unit(self):
        self.assertTrue(tax.is_unit("acre"))
        self.assertTrue(tax.is_unit("acre", attr=None))
        self.assertTrue(tax.is_unit("acre", "unit_id"))
        self.assertFalse(tax.is_unit("acre", "unit_name"))
        self.assertFalse(tax.is_unit("acre", "id"))

        with self.assertRaises(ValueError):
            found = tax.is_unit("acre", "unit_nickname")
        with self.assertRaises(ValueError):
            found = tax.is_unit("acre", attr=14)

        self.assertTrue(tax.is_unit("oz"))
        self.assertTrue(tax.is_unit("rad"))
        self.assertFalse(tax.is_unit("acrre"))
        self.assertFalse(tax.is_unit("ozz"))
        self.assertFalse(tax.is_unit("rrad"))
        self.assertTrue(tax.is_unit("Acre"))
        self.assertTrue(tax.is_unit("Acre", "unit_name"))
        self.assertTrue(tax.is_unit("u00001", "id"))
        self.assertTrue(tax.is_unit("Ounce"))
        self.assertTrue(tax.is_unit("Radian"))
        self.assertFalse(tax.is_unit("acrre"))
        self.assertFalse(tax.is_unit("ozz"))
        self.assertFalse(tax.is_unit("rrad"))
        self.assertTrue(tax.is_unit("u00004"))
        self.assertFalse(tax.is_unit("x0004"))

    def test_get_unit(self):
        unit = tax.get_unit("VAh")

        # Test data types
        # TODO: checks for strings are commented out for Python 2.7 which fails
        # due to unicode issues, need a proper test for both 2.7 and 3.x.
        # self.assertIsInstance(unit.id, str)
        # self.assertIsInstance(unit.unit_id, str)
        # self.assertIsInstance(unit.unit_name, str)
        # self.assertIsInstance(unit.ns_unit, str)
        # self.assertIsInstance(unit.item_type, str)
        self.assertIsInstance(unit.item_type_date, datetime.date)
        # self.assertIsInstance(unit.symbol, str)
        # self.assertIsInstance(unit.definition, str)
        self.assertIsInstance(unit.base_standard, taxonomy.BaseStandard)
        self.assertIsInstance(unit.status, taxonomy.UnitStatus)
        self.assertIsInstance(unit.version_date, datetime.date)

        # Test values
        self.assertEqual(unit.id, "u00291")
        self.assertEqual(unit.unit_id, "VAh")
        self.assertEqual(unit.unit_name, "Volt-ampere-hours")
        self.assertEqual(unit.ns_unit, "http://www.xbrl.org/2009/utr")
        self.assertEqual(unit.item_type, "energyItemType")
        self.assertEqual(unit.item_type_date, datetime.date(2009, 12, 16))
        self.assertEqual(unit.symbol, "VAh")
        self.assertEqual(unit.definition, "Volt-ampere (VA) hours of energy.")
        self.assertEqual(unit.base_standard, taxonomy.BaseStandard.customary)
        self.assertEqual(unit.status, taxonomy.UnitStatus.cr)
        self.assertEqual(unit.version_date, datetime.date(2017, 7, 12))

        unit2 = tax.get_unit("u00291")
        self.assertEqual(unit, unit2)
        unit3 = tax.get_unit("Volt-ampere-hours")
        self.assertEqual(unit, unit3)

    def test_get_all_units(self):
        units = tax.get_all_units()
        self.assertIsInstance(units, dict)
        self.assertEqual(len(units.keys()), 296)
