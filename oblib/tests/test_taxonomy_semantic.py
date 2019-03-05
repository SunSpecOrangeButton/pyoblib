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
from six import string_types
from oblib import taxonomy


taxonomy_obj = taxonomy.Taxonomy()
tax = taxonomy_obj.semantic


class TestTaxonomySemantic(unittest.TestCase):

    def test_concept_details(self):

        # Data type checks
        ci = tax.get_concept_details("solar:ACDisconnectSwitchMember")
        self.assertIsNotNone(ci)
        self.assertIsInstance(ci.abstract, bool)
        self.assertIsInstance(ci.id, string_types)
        # 'six.string_types' is equivalent to "str or unicode" in python2, "str" in python3
        self.assertIsInstance(ci.name, string_types)
        self.assertIsInstance(ci.nillable, bool)
        self.assertIsInstance(ci.period_independent, bool)
        self.assertIsInstance(ci.substitution_group, taxonomy.SubstitutionGroup)
        self.assertIsInstance(ci.type_name, string_types)
        self.assertIsInstance(ci.period_type, taxonomy.PeriodType)

        ci = tax.get_concept_details("solar:ACDisconnectSwitchMember")
        self.assertIsNotNone(ci)
        self.assertTrue(ci.abstract)
        self.assertEqual(ci.id, "solar:ACDisconnectSwitchMember")
        self.assertEqual(ci.name, "ACDisconnectSwitchMember")
        self.assertTrue(ci.nillable)
        self.assertFalse(ci.period_independent)
        self.assertEqual(ci.substitution_group, taxonomy.SubstitutionGroup.item)
        self.assertEqual(ci.type_name, "nonnum:domainItemType")
        self.assertEqual(ci.period_type, taxonomy.PeriodType.duration)

        # Values checks
        ci = tax.get_concept_details("solar:AdvisorInvoicesCounterparties")
        self.assertIsNotNone(ci)
        self.assertFalse(ci.abstract)
        self.assertEqual(ci.id, "solar:AdvisorInvoicesCounterparties")
        self.assertEqual(ci.name, "AdvisorInvoicesCounterparties")
        self.assertTrue(ci.nillable)
        self.assertFalse(ci.period_independent)
        self.assertEqual(ci.substitution_group, taxonomy.SubstitutionGroup.item)
        self.assertEqual(ci.type_name, "xbrli:stringItemType")
        self.assertEqual(ci.period_type, taxonomy.PeriodType.duration)

        ci = tax.get_concept_details("dei:LegalEntityIdentifier")
        self.assertIsNotNone(ci)
        self.assertFalse(ci.abstract)
        self.assertEqual(ci.id, "dei:LegalEntityIdentifier")
        self.assertEqual(ci.name, "LegalEntityIdentifier")
        self.assertTrue(ci.nillable)
        self.assertFalse(ci.period_independent)
        self.assertEqual(ci.substitution_group, taxonomy.SubstitutionGroup.item)
        self.assertEqual(ci.type_name, "dei:legalEntityIdentifierItemType")
        self.assertEqual(ci.period_type, taxonomy.PeriodType.duration)

        with self.assertRaises(KeyError):
            _ = tax.get_concept_details("solar:iamnotaconcept")

    def test_get_entrypoint_concepts(self):
        concepts = tax.get_entrypoint_concepts("MonthlyOperatingReport")
        self.assertEqual(85, len(concepts))
        concepts = tax.get_entrypoint_concepts("MonthlyOperatingReort")
        self.assertEqual(concepts, [])
        concepts, details = tax.get_entrypoint_concepts("CutSheet",
                                                        details=True)
        self.assertEqual(296, len(concepts))
        self.assertEqual(296, len(details))
        concepts, details = tax.get_entrypoint_concepts("Utility", True)
        self.assertEqual(len(concepts), 8)
        for ci in concepts:
            self.assertEqual(details[ci], tax.get_concept_details(ci))

        # TODO: SystemInstallation is currently loaded under System.
        # self.assertEqual(len(tax.concepts_ep("SystemInstallationCost")), 10)

# =============================================================================
#     def test_get_entrypoint_concepts_details(self):
#         self.assertEqual(len(tax.get_entrypoint_concepts_details("MonthlyOperatingReport")), 84)
#         self.assertEqual(tax.get_entrypoint_concepts_details("MonthlyOperatingReort"), None)
#         
#         # TODO: 302 is expected but 297 returned, seeking info on why this is from XBRL.
#         # self.assertEqual(len(tax.concepts_info_ep("CutSheet")), 302)
#         self.assertEqual(len(tax.get_entrypoint_concepts_details("CutSheet")), 297)
# 
#         self.assertEqual(len(tax.get_entrypoint_concepts_details("Utility")), 8)
# 
#         for ci in tax.get_entrypoint_concepts_details("Utility"):
#             self.assertEqual(ci, tax.get_concept_details(ci.id))
# 
# =============================================================================
    def test_get_all_concepts(self):
        self.assertIsNotNone(tax.get_all_concepts())
        self.assertIsInstance(tax.get_all_concepts(), list)
        self.assertIsNotNone(tax.get_all_concepts(details=True))
        self.assertIsNotNone(tax.get_all_concepts(details=True), dict)

    def test_get_all_type_names(self):
        self.assertEqual(92, len(tax.get_all_type_names()))

    def test_get_all_entrypoints(self):
        # 159 named entry points plus 1 for the "All" entry point:
        self.assertEqual(len(tax.get_all_entrypoints()), 160)

    def test_get_entrypoint_relationships(self):
        self.assertIsNone(tax.get_entrypoint_relationships("Arggh"))
        self.assertEqual(len(tax.get_entrypoint_relationships("Utility")), 7)
        self.assertEqual(85, len(tax.get_entrypoint_relationships("MonthlyOperatingReport")))
        self.assertEqual(300, len(tax.get_entrypoint_relationships("CutSheet")))

    def test_is_concept(self):
        self.assertTrue(tax.is_concept("solar:EnvironmentalImpactReportExpirationDate"))
        self.assertFalse(tax.is_concept("solar:EnvironmentalImpactReportExirationDate"))
        self.assertTrue(tax.is_concept("solar:AdvisorInvoicesCounterparties"))
        self.assertTrue(tax.is_concept("dei:LegalEntityIdentifier"))

    def test_is_entrypoint(self):
        self.assertTrue(tax.is_entrypoint("AssetManager"))
        self.assertFalse(tax.is_entrypoint("AssetMnager"))
        self.assertTrue(tax.is_entrypoint("MonthlyOperatingReport"))
        self.assertFalse(tax.is_entrypoint("MonthlyOperatingRepot"))

    def test_unrequired_concepts_removed(self):
        """
        In order to save memory concepts that are not required should be removed from memory after the taxonomy
        is loaded.  This primarily occurs in the us-gaap and dea namespaces since they are not always used
        by the solar namespace.  Thus these tests prove that certain concepts are gone.
        """

        self.assertFalse("dei:EntityReportingCurrencyISOCode" in tax._concepts_details)
        self.assertFalse("dei:BusinessContactMember" in tax._concepts_details)
        self.assertFalse("us-gaap:TimeSharingTransactionsAllowanceForUncollectibleAccountsOnReceivablesSoldWithRecourse" in tax._concepts_details)
        self.assertFalse("us-gaap:TreasuryStockValueAcquiredCostMethod" in tax._concepts_details)
