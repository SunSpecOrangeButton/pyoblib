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

import datetime
import unittest

from ..util import convert_taxonomy_xsd_bool, convert_taxonomy_xsd_date


class TestUtil(unittest.TestCase):

    def test_convert_taxonomy_xsd_bool(self):
        self.assertFalse(convert_taxonomy_xsd_bool(None))
        self.assertFalse(convert_taxonomy_xsd_bool("false"))
        self.assertFalse(convert_taxonomy_xsd_bool("False"))
        self.assertFalse(convert_taxonomy_xsd_bool("FALSE"))
        self.assertFalse(convert_taxonomy_xsd_bool("0"))
        self.assertFalse(convert_taxonomy_xsd_bool(""))
        self.assertTrue(convert_taxonomy_xsd_bool("true"))
        self.assertTrue(convert_taxonomy_xsd_bool("True"))
        self.assertTrue(convert_taxonomy_xsd_bool("TRUE"))
        self.assertTrue(convert_taxonomy_xsd_bool("1"))

    def test_convert_taxonomy_xsd_date(self):
        self.assertIsInstance(convert_taxonomy_xsd_date("2018-10-12"), datetime.date)
        self.assertIsNone(convert_taxonomy_xsd_date("201-10-12"), datetime.date)
        self.assertIsNone(convert_taxonomy_xsd_date("2019-42-12"), datetime.date)
        self.assertIsNone(convert_taxonomy_xsd_date("2019-11-32"), datetime.date)

        d = datetime.date(2017, 2, 14)
        self.assertEqual(convert_taxonomy_xsd_date("2017-02-14"), d)
        self.assertNotEqual(convert_taxonomy_xsd_date("2017-02-15"), d)
        self.assertNotEqual(convert_taxonomy_xsd_date("2017-03-14"), d)
        self.assertNotEqual(convert_taxonomy_xsd_date("2018-02-14"), d)
