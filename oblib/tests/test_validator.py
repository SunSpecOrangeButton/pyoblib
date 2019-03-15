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
from oblib import identifier, taxonomy, validator

tax = taxonomy.Taxonomy()
validator = validator.Validator(tax)


class TestValidator(unittest.TestCase):

    def test_validate_concept_value(self):
        concept = taxonomy.ConceptDetails()
        concept.id = "SomeId"
        concept.nillable = False
        self.assertEqual(1, len(validator.validate_concept_value(concept, None)[1]))
        concept.nillable = True
        self.assertEqual(0, len(validator.validate_concept_value(concept, None)[1]))

        concept.type_name = "xbrli:booleanItemType"
        self.assertEqual(1, len(validator.validate_concept_value(concept, "Arf")[1]))
        self.assertEqual(1, len(validator.validate_concept_value(concept, 52)[1]))
        self.assertEqual(0, len(validator.validate_concept_value(concept, False)[1]))
        self.assertEqual(0, len(validator.validate_concept_value(concept, True)[1]))
        self.assertEqual(0, len(validator.validate_concept_value(concept, "False")[1]))
        self.assertEqual(0, len(validator.validate_concept_value(concept, "True")[1]))
        self.assertEqual(0, len(validator.validate_concept_value(concept, "false")[1]))
        self.assertEqual(0, len(validator.validate_concept_value(concept, "true")[1]))

        concept.type_name = "xbrli:integerItemType"
        self.assertEqual(1, len(validator.validate_concept_value(concept, "Arf")[1]))
        # TODO: True value can be converted to integer value 1
        self.assertEqual(0, len(validator.validate_concept_value(concept, True)[1]))
        self.assertEqual(0, len(validator.validate_concept_value(concept, 52)[1]))
        self.assertEqual(0, len(validator.validate_concept_value(concept, -52)[1]))

        concept.type_name = "xbrli:stringItemType"
        self.assertEqual(0, len(validator.validate_concept_value(concept, False)[1]))
        self.assertEqual(0, len(validator.validate_concept_value(concept, 52)[1]))
        self.assertEqual(0, len(validator.validate_concept_value(concept, "Arf")[1]))
        self.assertEqual(0, len(validator.validate_concept_value(concept, "")[1]))

        concept.id = "SomeIdentifier"
        self.assertEqual(1, len(validator.validate_concept_value(concept, "Arf")[1]))
        self.assertEqual(0, len(validator.validate_concept_value(concept, identifier.identifier())[1]))

    def test_get_validator_method_name(self):
        type_name = "xbrli:booleanItemType"
        method_name_expected = "_xbrli_boolean_item_type_validator"
        method_name_result = validator._get_validator_method_name(type_name)
        self.assertEqual(method_name_expected, method_name_result)

    def test_xbrli_boolean_item_type_validator(self):
        values = {True: (True, []), 'True': (True, []), 'true': (True, []),
                  '1': (True, []), False: (False, []), 'False': (False, []),
                  '0': (False, []),
                  6: (6, ["'{}' is not a valid boolean value.".format(6)]),
                  5.1: (5.1, ["'{}' is not a valid boolean value.".format(5.1)]),
                  'foo': ('foo', ["'{}' is not a valid boolean value.".format('foo')])}
        for v in values.keys():
            result = validator._xbrli_boolean_item_type_validator(v)
            self.assertEqual(result[0], values[v][0])
            if values[v][1]:  # error messages are present
                self.assertTrue(result[1])
            else:
                self.assertFalse(result[1])

    def test_xbrli_string_item_type_validator(self):
        values = {'frog': ('frog', []), 'Frog': ('Frog', []),
                  True: ('True', []), 0.3: ('0.3', [])}
        for v in values.keys():
            result = validator._xbrli_string_item_type_validator(v)
            self.assertEqual(result[0], values[v][0])
            if values[v][1]:  # error messages are present
                self.assertTrue(result[1])
            else:
                self.assertFalse(result[1])

    def test_xbrli_integer_item_type_validator(self):
        values = {6: (6, []), '5': (5, []), True: (1, []),
                  'a': ('a', ["'{}' is not a valid integer value.".format('a')]),
                  5.1: (5.1, ["'{}' is not a valid integer value.".format(5.1)])}
        for v in values.keys():
            result = validator._xbrli_integer_item_type_validator(v)
            self.assertEqual(result[0], values[v][0])
            if values[v][1]:  # error messages are present
                self.assertTrue(result[1])
            else:
                self.assertFalse(result[1])
