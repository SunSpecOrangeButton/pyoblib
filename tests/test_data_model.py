# Copyright 2018 Jonathan Xia

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
from data_model import Entrypoint

class TestDataModelEntrypoint(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_instantiate_empty_entrypoint(self):
        doc = Entrypoint("CutSheet")

        # The newly initialized CutSheet should have a correct list of
        # allowable concepts as defined by the taxonomy for CutSheets:
        concepts = doc.allowedConcepts()
        # TypeOfDevice is allowed in CutSheets:
        self.assertIn('solar:TypeOfDevice', concepts)
        # AppraisalCounterparties is not allowed in CutSheets:
        self.assertNotIn('solar:AppraisalCounterparties', concepts)

        # The newly initialized CutSheet should have a correct list of tables
        # and each table should have a correct list of axes, as defined by
        # the taxonomy for CutSheets:
        tables = doc.getTableNames()
        self.assertItemsEqual(tables, ["solar:InverterPowerLevelTable",
                                       "solar:CutSheetDetailsTable"])
        self.assertItemsEqual(doc.getTable("solar:InverterPowerLevelTable").axes(),
                             ["solar:ProductIdentifierAxis",
                              "solar:InverterPowerLevelPercentAxis"])
        self.assertItemsEqual(doc.getTable("solar:CutSheetDetailsTable").axes(),
                              ["solar:ProductIdentifierAxis",
                               "solar:TestConditionAxis"])

    def test_get_table_for_concept(self):
        doc = Entrypoint("CutSheet")
        # The CutSheet instance should know that RevenueMeterFrequency
        # is a concept that belongs in the CutSheetDetailsTable
        table = doc.getTableForConcept("solar:RevenueMeterFrequency")
        self.assertEqual(table.name(), "solar:CutSheetDetailsTable")

        table = doc.getTableForConcept("solar:InverterEfficiencyAtVmaxPercent")
        self.assertEqual(table.name(), "solar:InverterPowerLevelTable")

        # but if we ask for something that is not a line item concept,
        # getTableForConcept should return None:
        table = doc.getTableForConcept("solar:CutSheetDetailsTable")
        self.assertIsNone(table)

        for concept_name in doc.all_my_concepts.keys():
            table = doc.getTableForConcept(concept_name)
            if table is not None:
                print "{} belongs in {}".format(concept_name, table.name())


    def test_can_write_concept(self):
        doc = Entrypoint("CutSheet")

        # Not every concept is writable. For instance, we shouldn't be able
        # to write a value for an Abstract concept, a LineItem group, an Axis,
        # a Domain, etc. even though those are part of this entrypoint.
        self.assertFalse( doc.canWriteConcept('solar:ProductIdentifierModuleAbstract'))
        self.assertTrue( doc.canWriteConcept('solar:TypeOfDevice'))
        self.assertFalse( doc.canWriteConcept('solar:CutSheetDetailsLineItems'))

        self.assertFalse( doc.canWriteConcept('solar:CutSheetDetailsTable'))
        self.assertFalse( doc.canWriteConcept('solar:TestConditionDomain'))

        self.assertFalse( doc.canWriteConcept('solar:ProductIdentifierAxis'))
        self.assertTrue( doc.canWriteConcept('solar:ProductIdentifier'))

