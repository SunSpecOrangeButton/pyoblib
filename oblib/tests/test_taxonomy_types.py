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

import unittest
from oblib import taxonomy_types


tax = taxonomy_types.TaxonomyTypes()


class TestTaxonomyTypes(unittest.TestCase):

    def test_get_all_types(self):
        self.assertEqual(67, len(tax.get_all_types()))

    def test_is_type(self):
        self.assertTrue(tax.is_type("solar-types:systemAvailabilityModeItemType"))
        self.assertTrue(tax.is_type("solar-types:deviceItemType"))
        self.assertTrue(tax.is_type("solar-types:insuranceItemType"))
        self.assertFalse(tax.is_type("solar:insuranceItemType"))
        self.assertFalse(tax.is_type("insuranceItemType"))
        self.assertFalse(tax.is_type("solar-types:systemAvailabilityMoeItemType"))
        self.assertFalse(tax.is_type("solar-types:deviceIteType"))
        self.assertFalse(tax.is_type("solar-types:inuranceItemType"))

    def test_get_type_enum(self):
        self.assertEqual(len(tax.get_type_enum("solar-types:projectAssetTypeItemType")), 3)
        self.assertEqual(len(tax.get_type_enum("solar-types:feeStatusItemType")), 5)
        self.assertEqual(len(tax.get_type_enum("solar-types:financialTransactionItemType")), 26)
        self.assertIsNone(tax.get_type_enum("solar-types:fdsfdsadsf"))
