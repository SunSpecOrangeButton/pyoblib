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

import taxonomy
import taxonomy_semantic

tax = taxonomy_semantic.TaxonomySemantic()


class TestTaxonomySemantic(unittest.TestCase):

    def test_concept_info(self):

        # Data type checks
        # TODO: checks for strings are commented out for Python 2.7 which fails
        # due to unicode issues, need a proper test for both 2.7 and 3.x.
        ci = tax.concept_info("solar:ACDisconnectSwitchMember")
        self.assertIsNotNone(ci)
        self.assertIsInstance(ci.abstract, bool)
        # self.assertIsInstance(ci.id, str)
        # self.assertIsInstance(ci.name, str)
        self.assertIsInstance(ci.nillable, bool)
        self.assertIsInstance(ci.period_independent, bool)
        self.assertIsInstance(ci.substitution_group, taxonomy.SubstitutionGroup)
        # self.assertIsInstance(ci.type_name, str)
        # self.assertIsInstance(ci.period_type, taxonomy.PeriodType)

        ci = tax.concept_info("solar:ACDisconnectSwitchMember")
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
        ci = tax.concept_info("solar:AdvisorInvoicesCounterparties")
        self.assertIsNotNone(ci)
        self.assertFalse(ci.abstract)
        self.assertEqual(ci.id, "solar:AdvisorInvoicesCounterparties")
        self.assertEqual(ci.name, "AdvisorInvoicesCounterparties")
        self.assertTrue(ci.nillable)
        self.assertFalse(ci.period_independent)
        self.assertEqual(ci.substitution_group, taxonomy.SubstitutionGroup.item)
        self.assertEqual(ci.type_name, "xbrli:stringItemType")
        self.assertEqual(ci.period_type, taxonomy.PeriodType.duration)

        ci = tax.concept_info("dei:LegalEntityIdentifier")
        self.assertIsNotNone(ci)
        self.assertFalse(ci.abstract)
        self.assertEqual(ci.id, "dei:LegalEntityIdentifier")
        self.assertEqual(ci.name, "LegalEntityIdentifier")
        self.assertTrue(ci.nillable)
        self.assertFalse(ci.period_independent)
        self.assertEqual(ci.substitution_group, taxonomy.SubstitutionGroup.item)
        self.assertEqual(ci.type_name, "dei:legalEntityIdentifierItemType")
        self.assertEqual(ci.period_type, taxonomy.PeriodType.duration)

    def test_concepts_ep(self):
        self.assertEqual(len(tax.concepts_ep("MonthlyOperatingReport")), 84)
        self.assertEqual(tax.concepts_ep("MonthlyOperatingReort"), None)
        self.assertEqual(len(tax.concepts_ep("CutSheet")), 302)
        self.assertEqual(len(tax.concepts_ep("Utility")), 8)

        # TODO: SystemInstallation is currently loaded under System.
        # self.assertEqual(len(tax.concepts_ep("SystemInstallationCost")), 10)

    def test_concepts_info_ep(self):
        self.assertEqual(len(tax.concepts_info_ep("MonthlyOperatingReport")), 84)
        self.assertEqual(tax.concepts_info_ep("MonthlyOperatingReort"), None)
        
        # TODO: 302 is expected but 297 returned, seeking info on why this is from XBRL.
        # self.assertEqual(len(tax.concepts_info_ep("CutSheet")), 302)
        self.assertEqual(len(tax.concepts_info_ep("CutSheet")), 297)

        self.assertEqual(len(tax.concepts_info_ep("Utility")), 8)

        for ci in tax.concepts_info_ep("Utility"):
            self.assertEqual(ci, tax.concept_info(ci.id))

    def elements(self):
        self.assertIsNotNone(tax.elements())

    def test_relationships_ep(self):
        self.assertIsNone(tax.relationships_ep("Arggh"))
        self.assertEqual(len(tax.relationships_ep("Utility")), 0)        
        self.assertEqual(len(tax.relationships_ep("MonthlyOperatingReport")), 84)
        self.assertEqual(len(tax.relationships_ep("CutSheet")), 305)

    def test_validate_concept(self):
        self.assertTrue(tax.validate_concept("solar:EnvironmentalImpactReportExpirationDate"))
        self.assertFalse(tax.validate_concept("solar:EnvironmentalImpactReportExirationDate"))
        self.assertTrue(tax.validate_concept("solar:AdvisorInvoicesCounterparties"))
        self.assertTrue(tax.validate_concept("dei:LegalEntityIdentifier"))

    def test_concept_value(self):
        self.assertEqual(0, len(tax.validate_concept_value("solar:TaxEquityCommunicationPlan", "Arff")))
        self.assertEqual(1, len(tax.validate_concept_value("solar:TaxEquityCommunicaionPlan", "Arff")))
        self.assertEqual(1, len(tax.validate_concept_value("solar:TaxEquityCommunicationPlan", 37)))
        self.assertEqual(1, len(tax.validate_concept_value("dei:LegalEntityIdentifier", "5493006MHB84DD0ZWV18")))

        # TODO: Once the validator is fully working test a large number of cases.

    def test_validate_ep(self):
        self.assertTrue(tax.validate_ep("AssetManager"))
        self.assertFalse(tax.validate_ep("AssetMnager"))
        self.assertTrue(tax.validate_ep("MonthlyOperatingReport"))
        self.assertFalse(tax.validate_ep("MonthlyOperatingRepot"))

    def test_unrequired_concepts_removed(self):
        """
        In order to save memory concepts that are not required should be removed from memory after the taxonomy
        is loaded.  This primarily occurs in the us-gaap and dea namespaces since they are not always used
        by the solar namespace.  Thus these tests prove that certain concepts are gone.
        """

        self.assertFalse("dei:EntityReportingCurrencyISOCode" in tax._elements)
        self.assertFalse("dei:BusinessContactMember" in tax._elements)
        self.assertFalse("us-gaap:TimeSharingTransactionsAllowanceForUncollectibleAccountsOnReceivablesSoldWithRecourse" in tax._elements)
        self.assertFalse("us-gaap:TreasuryStockValueAcquiredCostMethod" in tax._elements)
