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

import identifier
import taxonomy
import validator


class TestValidator(unittest.TestCase):

    def test_validate_concept_value(self):
        concept = taxonomy.Element()
        concept.id = "SomeId"
        concept.nillable = False
        self.assertEqual(1, len(validator.validate_concept_value(concept, None)))
        concept.nillable = True
        self.assertEqual(0, len(validator.validate_concept_value(concept, None)))

        concept.type_name = "xbrli:booleanItemType"
        self.assertEqual(1, len(validator.validate_concept_value(concept, "Arf")))
        self.assertEqual(1, len(validator.validate_concept_value(concept, 52)))
        self.assertEqual(0, len(validator.validate_concept_value(concept, False)))
        self.assertEqual(0, len(validator.validate_concept_value(concept, True)))
        self.assertEqual(0, len(validator.validate_concept_value(concept, "False")))
        self.assertEqual(0, len(validator.validate_concept_value(concept, "True")))
        self.assertEqual(0, len(validator.validate_concept_value(concept, "false")))
        self.assertEqual(0, len(validator.validate_concept_value(concept, "true")))

        concept.type_name = "xbrli:integerItemType"
        self.assertEqual(1, len(validator.validate_concept_value(concept, "Arf")))
        self.assertEqual(1, len(validator.validate_concept_value(concept, True)))
        self.assertEqual(0, len(validator.validate_concept_value(concept, 52)))
        self.assertEqual(0, len(validator.validate_concept_value(concept, -52)))

        concept.type_name = "xbrli:stringItemType"
        self.assertEqual(1, len(validator.validate_concept_value(concept, False)))
        self.assertEqual(1, len(validator.validate_concept_value(concept, 52)))
        self.assertEqual(0, len(validator.validate_concept_value(concept, "Arf")))
        self.assertEqual(0, len(validator.validate_concept_value(concept, "")))

        concept.id = "SomeIdentifier"
        self.assertEqual(1, len(validator.validate_concept_value(concept, "Arf")))
        self.assertEqual(0, len(validator.validate_concept_value(concept, identifier.identifier())))


    def test_get_validator_method_name(self):
        type_name = "xbrli:booleanItemType"
        method_name_expected = "xbrli_boolean_item_type_validator"
        method_name_result = validator.get_validator_method_name(type_name)
        self.assertEqual(method_name_expected, method_name_result)