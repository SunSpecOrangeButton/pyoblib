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
from oblib import identifier


class TestIdentifier(unittest.TestCase):
    def test_valid_identifiers(self):
        # UUID1.
        self.assertTrue(identifier.validate('70e7cfc6-def7-11e8-bb65-10e7c6792ac1'))

        # UUID3.
        self.assertTrue(identifier.validate('a402d082-1bb6-38ce-b44e-953fd8610fac'))

        # UUID4.
        self.assertTrue(identifier.validate('9c189dd1-a4d3-4b3f-ba08-37fc962dc9c9'))

        # UUID5.
        self.assertTrue(identifier.validate('76c439e1-dfc9-50ab-a06a-d70afa21bb2f'))

        # UUID are case insensitive.
        self.assertTrue(identifier.validate('9C189DD1-A4D3-4B3F-BA08-37FC962DC9C9'))

    def test_invalid_identifier_bad_version(self):
        # Not a valid UUID identifier (the third group should start with 1, 2, 3, 4 or 5).
        self.assertFalse(identifier.validate('9c189dd1-a4d3-Xb3f-ba08-37fc962dc9c9'))

    def test_invalid_identifier_format(self):
        # Bad UUID format
        self.assertFalse(identifier.validate("dfasfdfsadfds"))
