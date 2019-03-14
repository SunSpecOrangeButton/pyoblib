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
from oblib import ob


class TestOb(unittest.TestCase):

    def test_ob_errors(self):
        self.assertIsInstance(ob.OBError("test message"), ob.OBError)
        self.assertIsInstance(ob.OBTypeError("test message"), ob.OBTypeError)
        self.assertIsInstance(ob.OBContextError("test message"), ob.OBContextError)
        self.assertIsInstance(ob.OBConceptError("test message"), ob.OBConceptError)
        self.assertIsInstance(ob.OBNotFoundError("test message"), ob.OBNotFoundError)
        self.assertIsInstance(ob.OBUnitError("test message"), ob.OBUnitError)
        self.assertIsInstance(ob.OBValidationError("test message"), ob.OBValidationError)


    def test_ob_multiple_errors(self):

        # Test basic case
        errors = ob.OBMultipleErrors(ob.OBError("Multiple errors test"))
        errors.append(ob.OBError("message 1"))
        errors.append(ob.OBError("message 2"))
        errors.append(ob.OBError("message 3"))
        self.assertEqual("Multiple errors test", (str(errors)))
        self.assertEqual(3, len(errors.get_errors()))
        self.assertEqual("message 1", str(errors.get_errors()[0]))
        self.assertEqual("message 2", str(errors.get_errors()[1]))
        self.assertEqual("message 3", str(errors.get_errors()[2]))

        # Test appending a string
        errors = ob.OBMultipleErrors(ob.OBError("Multiple errors test"))
        errors.append("message")
        self.assertIsInstance(errors.get_errors()[0], ob.OBError)
        self.assertEqual("message", str(errors.get_errors()[0]))

        # Test concatenating two lists
        errors = ob.OBMultipleErrors(ob.OBError("Multiple errors found"))
        errors.append("message")
        errors.append("message")
        errors2 = ob.OBMultipleErrors(ob.OBError("Multiple errors found"))
        errors2.append("message")
        errors2.append("message")
        errors.append(errors2)
        self.assertEqual(4, len(errors.get_errors()))