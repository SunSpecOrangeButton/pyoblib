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

import unittest

from ..taxonomy import Unit, Element, Relationship, Taxonomy
from ..taxonomy_semantic import TaxonomySemantic
from ..taxonomy_types import TaxonomyTypes
from ..taxonomy_units import TaxonomyUnits
from ..taxonomy_misc import TaxonomyNumericTypes, TaxonomyGenericRoles, TaxonomyRefParts


class TestTaxonomy(unittest.TestCase):

    def test_unit(self):
        self.assertIsInstance(Unit(), Unit)

    def test_element(self):
        self.assertIsInstance(Element(), Element)

    def test_relationship(self):
        self.assertIsInstance(Relationship(), Relationship)

    def test_taxonomy(self):
        tax = Taxonomy()
        self.assertIsInstance(tax, Taxonomy)
        self.assertIsInstance(tax.semantic, TaxonomySemantic)
        self.assertIsInstance(tax.types, TaxonomyTypes)
        self.assertIsInstance(tax.units, TaxonomyUnits)
        self.assertIsInstance(tax.numeric_types, TaxonomyNumericTypes)
        self.assertIsInstance(tax.generic_roles, TaxonomyGenericRoles)
        self.assertIsInstance(tax.ref_parts, TaxonomyRefParts)
