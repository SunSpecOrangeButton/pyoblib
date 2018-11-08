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
        tables = doc.getTables()
        self.assertEqual(tables[0].name(), "solar:InverterPowerLevelTable")
        self.assertEqual(tables[1].name(), "solar:CutSheetDetailsTable")

        self.assertItemsEqual(tables[0].axes(),
                             ["solar:ProductIdentifierAxis",
                              "solar:InverterPowerLevelPercentAxis"])
        self.assertItemsEqual(tables[1].axes(),
                              ["solar:ProductIdentifierAxis",
                               "solar:TestConditionAxis"])
