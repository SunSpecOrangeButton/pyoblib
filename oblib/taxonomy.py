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

import taxonomy_semantic
import taxonomy_types
import taxonomy_units
import taxonomy_misc


class Element(object):
    """
    Element is used to model a data element within a Taxonomy Concept.
    """

    def __init__(self):
        self.abstract = None
        self.id = None
        self.name = None
        self.nillable = None
        self.period_independent = None
        self.substitution_group = None
        self.type_name = None
        self.period_type = None

    def __repr__(self):
        return "{" + str(self.abstract) + \
            "," + str(self.id) + \
            "," + str(self.name) + \
            "," + str(self.nillable) + \
            "," + str(self.period_independent) + \
            "," + str(self.substitution_group) + \
            "," + str(self.type_name) + \
            "," + str(self.period_type) + \
            "}"


class Unit(object):
    """
    Unit holds the definition of a Unit from the Unit Registry.
    """

    def __init__(self):
        self.id = None
        self.unit_id = None
        self.unit_name = None
        self.ns_unit = None
        self.item_type = None
        self.item_type_date = None
        self.symbol = None
        self.definition = None
        self.base_standard = None
        self.status = None
        self.version_date = None

    def __repr__(self):
        return "{" + str(self.id) + \
            "," + str(self.unit_id) + \
            "," + str(self.unit_name) + \
            "," + str(self.ns_unit) + \
            "," + str(self.item_type) + \
            "," + str(self.item_type_date) + \
            "," + str(self.symbol) + \
            "," + str(self.definition) + \
            "," + str(self.base_standard) + \
            "," + str(self.status) + \
            "," + str(self.version_date) + \
            "}"


class Taxonomy(object):
    """
    Parent class for Taxonomy.  Use this to load and access all elements
    of the Taxonomy simultaneously.  Generally speaking this supplies
    a single import location and is better than loading just a portion
    of the Taxonomy unless there is a specific need to save memory.
    """

    def __init__(self):
        self.semantic = taxonomy_semantic.TaxonomySemantic()
        self.types = taxonomy_types.TaxonomyTypes()
        self.units = taxonomy_units.TaxonomyUnits()
        self.misc = taxonomy_misc.TaxonomyMisc()


# Accessor for singleton Taxonomy object:
m_singletonTaxonomy = None
def getTaxonomy():
    global m_singletonTaxonomy
    if m_singletonTaxonomy is None:
        m_singletonTaxonomy = Taxonomy()
    return m_singletonTaxonomy
