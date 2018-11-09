# Copyright 2018 Wells Fargo

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
import taxonomy_types

tax = taxonomy_types.TaxonomyTypes()


class TestTaxonomyTypes(unittest.TestCase):

    def test_taxonomy_types(self):
        self.assertEqual(len(tax.types()), 65)

    def test_taxonomy_types_validate_type(self):
        self.assertTrue(tax.validate_type("systemAvailabilityModeItemType"))
        self.assertTrue(tax.validate_type("deviceItemType"))
        self.assertTrue(tax.validate_type("insuranceItemType"))
        self.assertFalse(tax.validate_type("systemAvailabilityMoeItemType"))
        self.assertFalse(tax.validate_type("deviceIteType"))
        self.assertFalse(tax.validate_type("inuranceItemType"))

    def test_taxonomy_types_type_enum(self):
        self.assertEqual(len(tax.type_enum("projectAssetTypeItemType")), 3)
        self.assertEqual(len(tax.type_enum("feeStatusItemType")), 5)
        self.assertEqual(len(tax.type_enum("financialTransactionItemType")), 26)
        self.assertIsNone(tax.type_enum("fdsfdsadsf"))
