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
from oblib import taxonomy_misc


tax_numeric_types = taxonomy_misc.TaxonomyNumericTypes()
tax_generic_roles = taxonomy_misc.TaxonomyGenericRoles()
tax_ref_parts = taxonomy_misc.TaxonomyRefParts()
tax_doc = taxonomy_misc.TaxonomyDocumentation()


class TestTaxonomyMisc(unittest.TestCase):

    def test_get_all_numeric_types(self):
        self.assertEqual(len(tax_numeric_types.get_all_numeric_types()), 13)

    def test_get_all_ref_parts(self):
        self.assertEqual(len(tax_ref_parts.get_all_ref_parts()), 6)

    def test_get_all_generic_roles(self):
        self.assertEqual(len(tax_generic_roles.get_all_generic_roles()), 5)

    def test_validate_numeric_types(self):
        self.assertTrue(tax_numeric_types.is_numeric_type("num-us:insolationItemType"))
        self.assertTrue(tax_numeric_types.is_numeric_type("num-us:speedItemType"))
        self.assertTrue(tax_numeric_types.is_numeric_type("num-us:luminousIntensityItemType"))
        self.assertFalse(tax_numeric_types.is_numeric_type("solar:luminousIntensityItemType"))
        self.assertFalse(tax_numeric_types.is_numeric_type("luminousIntensityItemType"))
        self.assertFalse(tax_numeric_types.is_numeric_type("num-us:inslationItemType"))
        self.assertFalse(tax_numeric_types.is_numeric_type("num-us:speedItemTye"))
        self.assertFalse(tax_numeric_types.is_numeric_type("num-us:luminousIntensityIteType"))

    def test_is_ref_part(self):
        self.assertTrue(tax_ref_parts.is_ref_part("Publisher"))
        self.assertTrue(tax_ref_parts.is_ref_part("Sample"))
        self.assertTrue(tax_ref_parts.is_ref_part("Confidentiality"))
        self.assertFalse(tax_ref_parts.is_ref_part("Publishe"))
        self.assertFalse(tax_ref_parts.is_ref_part("Sampl"))
        self.assertFalse(tax_ref_parts.is_ref_part("Confidentialit"))

    def test_is_generic_role(self):
        self.assertTrue(tax_generic_roles.is_generic_role("Generic UML aggregation arc"))
        self.assertTrue(tax_generic_roles.is_generic_role("Generic UML inheritance arc"))
        self.assertTrue(tax_generic_roles.is_generic_role("Generic UML property arc"))
        self.assertFalse(tax_generic_roles.is_generic_role("Genric UML aggregation arc"))
        self.assertFalse(tax_generic_roles.is_generic_role("Genric UML inheritance arc"))
        self.assertFalse(tax_generic_roles.is_generic_role("Genric UML property arc"))

    def test_get_all_concepts_documentation(self):
        self.assertEqual(tax_doc.get_all_concepts_documentation()["solar:EntitySizeACPower"],
                             "Size of the entity in megawatts AC.")
        self.assertEqual(tax_doc.get_all_concepts_documentation()["solar:FundDescriptionAnalyst"],
                             "Name of analyst covering the fund.")
        self.assertEqual(tax_doc.get_all_concepts_documentation()["solar:IncentivesPerformanceBasedIncentiveEscalator"],
                             "Annual escalation of the performance based incentive value (percent)")

    def test_get_concept_documentation(self):
        self.assertEqual(tax_doc.get_concept_documentation("solar:EntitySizeACPower"),
                          "Size of the entity in megawatts AC.")
        self.assertEqual(tax_doc.get_concept_documentation("solar:FundDescriptionAnalyst"),
                         "Name of analyst covering the fund.")
        self.assertEqual(tax_doc.get_concept_documentation("solar:IncentivesPerformanceBasedIncentiveEscalator"),
                         "Annual escalation of the performance based incentive value (percent)")
        self.assertIsNone(tax_doc.get_concept_documentation("solar:NotCorect"))
