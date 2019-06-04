# Copyright 2019 SunSpec Alliance

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
import datetime
from six import string_types

from oblib import taxonomy


tax = taxonomy.Taxonomy()


class TestTaxonomy(unittest.TestCase):

    def test_unit(self):
        self.assertIsInstance(taxonomy.Unit(), taxonomy.Unit)

    def test_element(self):
        self.assertIsInstance(taxonomy.ConceptDetails(), taxonomy.ConceptDetails)

    def test_relationship(self):
        self.assertIsInstance(taxonomy.Relationship(), taxonomy.Relationship)

    def test_taxonomy(self):
        self.assertIsInstance(tax, taxonomy.Taxonomy)
        self.assertIsInstance(tax.semantic, taxonomy.TaxonomySemantic)
        self.assertIsInstance(tax.types, taxonomy.TaxonomyTypes)
        self.assertIsInstance(tax.units, taxonomy.TaxonomyUnits)
        self.assertIsInstance(tax.numeric_types, taxonomy.TaxonomyNumericTypes)
        self.assertIsInstance(tax.generic_roles, taxonomy.TaxonomyGenericRoles)
        self.assertIsInstance(tax.ref_parts, taxonomy.TaxonomyRefParts)
        self.assertIsInstance(tax.documentation, taxonomy.TaxonomyDocumentation)


class TestTaxonomyNumericTypes(unittest.TestCase):

    def test_get_all_numeric_types(self):
        self.assertEqual(len(tax.numeric_types.get_all_numeric_types()), 13)

    def test_validate_numeric_types(self):
        self.assertTrue(tax.numeric_types.is_numeric_type("num-us:insolationItemType"))
        self.assertTrue(tax.numeric_types.is_numeric_type("num-us:speedItemType"))
        self.assertTrue(tax.numeric_types.is_numeric_type("num-us:luminousIntensityItemType"))
        self.assertFalse(tax.numeric_types.is_numeric_type("solar:luminousIntensityItemType"))
        self.assertFalse(tax.numeric_types.is_numeric_type("luminousIntensityItemType"))
        self.assertFalse(tax.numeric_types.is_numeric_type("num-us:inslationItemType"))
        self.assertFalse(tax.numeric_types.is_numeric_type("num-us:speedItemTye"))
        self.assertFalse(tax.numeric_types.is_numeric_type("num-us:luminousIntensityIteType"))


class TestTaxonomyRefParts(unittest.TestCase):

    def test_get_all_ref_parts(self):
        self.assertEqual(len(tax.ref_parts.get_all_ref_parts()), 6)

    def test_is_ref_part(self):
        self.assertTrue(tax.ref_parts.is_ref_part("Publisher"))
        self.assertTrue(tax.ref_parts.is_ref_part("Sample"))
        self.assertTrue(tax.ref_parts.is_ref_part("Confidentiality"))
        self.assertFalse(tax.ref_parts.is_ref_part("Publishe"))
        self.assertFalse(tax.ref_parts.is_ref_part("Sampl"))
        self.assertFalse(tax.ref_parts.is_ref_part("Confidentialit"))


class TestTaxonomyGenericRoles(unittest.TestCase):

    def test_get_all_generic_roles(self):
        self.assertEqual(len(tax.generic_roles.get_all_generic_roles()), 5)

    def test_is_generic_role(self):
        self.assertTrue(tax.generic_roles.is_generic_role("Generic UML aggregation arc"))
        self.assertTrue(tax.generic_roles.is_generic_role("Generic UML inheritance arc"))
        self.assertTrue(tax.generic_roles.is_generic_role("Generic UML property arc"))
        self.assertFalse(tax.generic_roles.is_generic_role("Genric UML aggregation arc"))
        self.assertFalse(tax.generic_roles.is_generic_role("Genric UML inheritance arc"))
        self.assertFalse(tax.generic_roles.is_generic_role("Genric UML property arc"))


class TextTaxonomyDocumentation(unittest.TestCase):

    def test_get_all_concepts_documentation(self):
        self.assertEqual(tax.documentation.get_all_concepts_documentation()["solar:EntitySizeACPower"],
                             "Size of the entity in megawatts AC.")
        self.assertEqual(tax.documentation.get_all_concepts_documentation()["solar:FundDescriptionAnalyst"],
                             "Name of analyst covering the fund.")
        self.assertEqual(tax.documentation.get_all_concepts_documentation()["solar:IncentivesPerformanceBasedIncentiveEscalator"],
                             "Annual escalation of the performance based incentive value (percent)")

    def test_get_concept_documentation(self):
        self.assertEqual(tax.documentation.get_concept_documentation("solar:EntitySizeACPower"),
                          "Size of the entity in megawatts AC.")
        self.assertEqual(tax.documentation.get_concept_documentation("solar:FundDescriptionAnalyst"),
                         "Name of analyst covering the fund.")
        self.assertEqual(tax.documentation.get_concept_documentation("solar:IncentivesPerformanceBasedIncentiveEscalator"),
                         "Annual escalation of the performance based incentive value (percent)")
        self.assertIsNone(tax.documentation.get_concept_documentation("solar:NotCorect"))


class TestTaxonomyTypes(unittest.TestCase):

    def test_get_all_types(self):
        self.assertEqual(67, len(tax.types.get_all_types()))

    def test_is_type(self):
        self.assertTrue(tax.types.is_type("solar-types:systemAvailabilityModeItemType"))
        self.assertTrue(tax.types.is_type("solar-types:deviceItemType"))
        self.assertTrue(tax.types.is_type("solar-types:insuranceItemType"))
        self.assertFalse(tax.types.is_type("solar:insuranceItemType"))
        self.assertFalse(tax.types.is_type("insuranceItemType"))
        self.assertFalse(tax.types.is_type("solar-types:systemAvailabilityMoeItemType"))
        self.assertFalse(tax.types.is_type("solar-types:deviceIteType"))
        self.assertFalse(tax.types.is_type("solar-types:inuranceItemType"))

    def test_get_type_enum(self):
        self.assertEqual(len(tax.types.get_type_enum("solar-types:projectAssetTypeItemType")), 3)
        self.assertEqual(len(tax.types.get_type_enum("solar-types:feeStatusItemType")), 5)
        self.assertEqual(len(tax.types.get_type_enum("solar-types:financialTransactionItemType")), 26)
        self.assertIsNone(tax.types.get_type_enum("solar-types:fdsfdsadsf"))


class TestTaxonomyUnits(unittest.TestCase):

    def test_is_unit(self):
        self.assertTrue(tax.units.is_unit("acre"))
        self.assertTrue(tax.units.is_unit("acre", attr=None))
        self.assertTrue(tax.units.is_unit("acre", "unit_id"))
        self.assertFalse(tax.units.is_unit("acre", "unit_name"))
        self.assertFalse(tax.units.is_unit("acre", "id"))

        with self.assertRaises(ValueError):
            found = tax.units.is_unit("acre", "unit_nickname")
        with self.assertRaises(ValueError):
            found = tax.units.is_unit("acre", attr=14)

        self.assertTrue(tax.units.is_unit("oz"))
        self.assertTrue(tax.units.is_unit("rad"))
        self.assertFalse(tax.units.is_unit("acrre"))
        self.assertFalse(tax.units.is_unit("ozz"))
        self.assertFalse(tax.units.is_unit("rrad"))
        self.assertTrue(tax.units.is_unit("Acre"))
        self.assertTrue(tax.units.is_unit("Acre", "unit_name"))
        self.assertTrue(tax.units.is_unit("u00001", "id"))
        self.assertTrue(tax.units.is_unit("Ounce"))
        self.assertTrue(tax.units.is_unit("Radian"))
        self.assertFalse(tax.units.is_unit("acrre"))
        self.assertFalse(tax.units.is_unit("ozz"))
        self.assertFalse(tax.units.is_unit("rrad"))
        self.assertTrue(tax.units.is_unit("u00004"))
        self.assertFalse(tax.units.is_unit("x0004"))

    def test_get_unit(self):
        unit = tax.units.get_unit("VAh")

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

        unit2 = tax.units.get_unit("u00291")
        self.assertEqual(unit, unit2)
        unit3 = tax.units.get_unit("Volt-ampere-hours")
        self.assertEqual(unit, unit3)

    def test_get_all_units(self):
        units = tax.units.get_all_units()
        self.assertIsInstance(units, dict)
        self.assertEqual(len(units.keys()), 296)


class TestTaxonomySemantic(unittest.TestCase):

    def test_concept_details(self):

        # Data type checks
        ci = tax.semantic.get_concept_details("solar:ACDisconnectSwitchMember")
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

        ci = tax.semantic.get_concept_details("solar:MonthlyPeriodAxis")
        self.assertIsNone(ci.typed_domain_ref)

        ci = tax.semantic.get_concept_details("solar:PVSystemIdentifierAxis")
        self.assertIsInstance(ci.typed_domain_ref, string_types)

        # Values checks
        ci = tax.semantic.get_concept_details("solar:ACDisconnectSwitchMember")
        self.assertIsNotNone(ci)
        self.assertTrue(ci.abstract)
        self.assertEqual(ci.id, "solar:ACDisconnectSwitchMember")
        self.assertEqual(ci.name, "ACDisconnectSwitchMember")
        self.assertTrue(ci.nillable)
        self.assertFalse(ci.period_independent)
        self.assertEqual(ci.substitution_group, taxonomy.SubstitutionGroup.item)
        self.assertEqual(ci.type_name, "nonnum:domainItemType")
        self.assertEqual(ci.period_type, taxonomy.PeriodType.duration)

        ci = tax.semantic.get_concept_details("solar:AdvisorInvoicesCounterparties")
        self.assertIsNotNone(ci)
        self.assertFalse(ci.abstract)
        self.assertEqual(ci.id, "solar:AdvisorInvoicesCounterparties")
        self.assertEqual(ci.name, "AdvisorInvoicesCounterparties")
        self.assertTrue(ci.nillable)
        self.assertFalse(ci.period_independent)
        self.assertEqual(ci.substitution_group, taxonomy.SubstitutionGroup.item)
        self.assertEqual(ci.type_name, "xbrli:stringItemType")
        self.assertEqual(ci.period_type, taxonomy.PeriodType.duration)

        ci = tax.semantic.get_concept_details("dei:LegalEntityIdentifier")
        self.assertIsNotNone(ci)
        self.assertFalse(ci.abstract)
        self.assertEqual(ci.id, "dei:LegalEntityIdentifier")
        self.assertEqual(ci.name, "LegalEntityIdentifier")
        self.assertTrue(ci.nillable)
        self.assertFalse(ci.period_independent)
        self.assertEqual(ci.substitution_group, taxonomy.SubstitutionGroup.item)
        self.assertEqual(ci.type_name, "dei:legalEntityIdentifierItemType")
        self.assertEqual(ci.period_type, taxonomy.PeriodType.duration)

        ci = tax.semantic.get_concept_details("solar:PVSystemIdentifierAxis")
        self.assertEqual(ci.typed_domain_ref, "#solar_PVSystemIdentifierDomain")

        with self.assertRaises(KeyError):
            _ = tax.semantic.get_concept_details("solar:iamnotaconcept")

    def test_get_entrypoint_concepts(self):
        concepts = tax.semantic.get_entrypoint_concepts("MonthlyOperatingReport")
        self.assertEqual(85, len(concepts))
        concepts = tax.semantic.get_entrypoint_concepts("MonthlyOperatingReort")
        self.assertEqual(concepts, [])
        concepts, details = tax.semantic.get_entrypoint_concepts("CutSheet",
                                                        details=True)
        self.assertEqual(296, len(concepts))
        self.assertEqual(296, len(details))
        concepts, details = tax.semantic.get_entrypoint_concepts("Utility", True)
        self.assertEqual(len(concepts), 8)
        for ci in concepts:
            self.assertEqual(details[ci], tax.semantic.get_concept_details(ci))

        # TODO: SystemInstallation is currently loaded under System.
        # self.assertEqual(len(tax.semantic.concepts_ep("SystemInstallationCost")), 10)

# =============================================================================
#     def test_get_entrypoint_concepts_details(self):
#         self.assertEqual(len(tax.semantic.get_entrypoint_concepts_details("MonthlyOperatingReport")), 84)
#         self.assertEqual(tax.semantic.get_entrypoint_concepts_details("MonthlyOperatingReort"), None)
#
#         # TODO: 302 is expected but 297 returned, seeking info on why this is from XBRL.
#         # self.assertEqual(len(tax.semantic.concepts_info_ep("CutSheet")), 302)
#         self.assertEqual(len(tax.semantic.get_entrypoint_concepts_details("CutSheet")), 297)
#
#         self.assertEqual(len(tax.semantic.get_entrypoint_concepts_details("Utility")), 8)
#
#         for ci in tax.semantic.get_entrypoint_concepts_details("Utility"):
#             self.assertEqual(ci, tax.semantic.get_concept_details(ci.id))
#
# =============================================================================
    def test_get_all_concepts(self):
        self.assertIsNotNone(tax.semantic.get_all_concepts())
        self.assertIsInstance(tax.semantic.get_all_concepts(), list)
        self.assertIsNotNone(tax.semantic.get_all_concepts(details=True))
        self.assertIsNotNone(tax.semantic.get_all_concepts(details=True), dict)

    def test_get_all_type_names(self):
        self.assertEqual(92, len(tax.semantic.get_all_type_names()))

    def test_get_all_entrypoints(self):
        # 159 named entry points plus 1 for the "All" entry point:
        self.assertEqual(len(tax.semantic.get_all_entrypoints()), 160)

    def test_get_entrypoint_relationships(self):
        self.assertIsNone(tax.semantic.get_entrypoint_relationships("Arggh"))
        self.assertEqual(len(tax.semantic.get_entrypoint_relationships("Utility")), 7)
        self.assertEqual(85, len(tax.semantic.get_entrypoint_relationships("MonthlyOperatingReport")))
        self.assertEqual(300, len(tax.semantic.get_entrypoint_relationships("CutSheet")))

    def test_is_concept(self):
        self.assertTrue(tax.semantic.is_concept("solar:EnvironmentalImpactReportExpirationDate"))
        self.assertFalse(tax.semantic.is_concept("solar:EnvironmentalImpactReportExirationDate"))
        self.assertTrue(tax.semantic.is_concept("solar:AdvisorInvoicesCounterparties"))
        self.assertTrue(tax.semantic.is_concept("dei:LegalEntityIdentifier"))

    def test_is_entrypoint(self):
        self.assertTrue(tax.semantic.is_entrypoint("AssetManager"))
        self.assertFalse(tax.semantic.is_entrypoint("AssetMnager"))
        self.assertTrue(tax.semantic.is_entrypoint("MonthlyOperatingReport"))
        self.assertFalse(tax.semantic.is_entrypoint("MonthlyOperatingRepot"))

    def test_unrequired_concepts_removed(self):
        """
        In order to save memory concepts that are not required should be removed from memory after the taxonomy
        is loaded.  This primarily occurs in the us-gaap and dea namespaces since they are not always used
        by the solar namespace.  Thus these tests prove that certain concepts are gone.
        """

        self.assertFalse("dei:EntityReportingCurrencyISOCode" in tax.semantic._concepts_details)
        self.assertFalse("dei:BusinessContactMember" in tax.semantic._concepts_details)
        self.assertFalse("us-gaap:TimeSharingTransactionsAllowanceForUncollectibleAccountsOnReceivablesSoldWithRecourse" in tax.semantic._concepts_details)
        self.assertFalse("us-gaap:TreasuryStockValueAcquiredCostMethod" in tax.semantic._concepts_details)
