# Copyright 2018 Wells Fargo

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

import identifier
import taxonomy
import validator


class TestCore(unittest.TestCase):

    def test_validate_concept_value(self):
        concept = taxonomy.Element()
        concept.id = "SomeId"
        concept.nillable = False
        self.assertFalse(validator.validate_concept_value(concept, None))
        concept.nillable = True
        self.assertTrue(validator.validate_concept_value(concept, None))

        concept.type_name = "xbrli:booleanItemType"
        self.assertFalse(validator.validate_concept_value(concept, "Arf"))
        self.assertFalse(validator.validate_concept_value(concept, 52))
        self.assertTrue(validator.validate_concept_value(concept, False))
        self.assertTrue(validator.validate_concept_value(concept, True))

        concept.type_name = "xbrli:integerItemType"
        self.assertFalse(validator.validate_concept_value(concept, "Arf"))
        self.assertFalse(validator.validate_concept_value(concept, True))
        self.assertTrue(validator.validate_concept_value(concept, -52))
        self.assertTrue(validator.validate_concept_value(concept, 52))

        concept.type_name = "xbrli:stringItemType"
        self.assertFalse(validator.validate_concept_value(concept, False))
        self.assertFalse(validator.validate_concept_value(concept, 52))
        self.assertTrue(validator.validate_concept_value(concept, "Arf"))
        self.assertTrue(validator.validate_concept_value(concept, ""))

        concept.id = "SomeIdentifier"
        self.assertFalse(validator.validate_concept_value(concept, "Arf"))
        self.assertTrue(validator.validate_concept_value(concept, identifier.identifier()))
