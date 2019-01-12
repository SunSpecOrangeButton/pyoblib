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

import taxonomy
import taxonomy_units

tax = taxonomy_units.TaxonomyUnits()


class TestTaxonomyUnits(unittest.TestCase):

    def test_taxonomy_units(self):
        self.assertEqual(len(tax.units()), 296)

    def test_validate_unit(self):
        self.assertTrue(tax.validate_unit(unit_id="acre"))
        self.assertTrue(tax.validate_unit(unit_id="oz"))
        self.assertTrue(tax.validate_unit(unit_id="rad"))
        self.assertFalse(tax.validate_unit(unit_id="acrre"))
        self.assertFalse(tax.validate_unit(unit_id="ozz"))
        self.assertFalse(tax.validate_unit(unit_id="rrad"))
        self.assertTrue(tax.validate_unit(unit_name="Acre"))
        self.assertTrue(tax.validate_unit(unit_name="Ounce"))
        self.assertTrue(tax.validate_unit(unit_name="Radian"))
        self.assertFalse(tax.validate_unit(unit_name="acrre"))
        self.assertFalse(tax.validate_unit(unit_name="ozz"))
        self.assertFalse(tax.validate_unit(unit_name="rrad"))

    def test_unit(self):
        unit = tax.unit("VAh")

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
