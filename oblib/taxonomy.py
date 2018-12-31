"""Handles Orange button taxonomy."""

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import enum

import taxonomy_semantic
import taxonomy_types
import taxonomy_units
import taxonomy_misc


class SubstitutionGroup(enum.Enum):
    """
    Legal values for substitution groups.
    """

    item = "xbrli:item"
    dimension = "xbrldt:dimensionItem"
    hypercube = "xbrldt:hypercubeItem"


class PeriodType(enum.Enum):
    """
    Legal values for period types.
    """

    duration = "duration"
    instant = "instant"


class BaseStandard(enum.Enum):
    """
    Legal values for base standards.
    """

    customary = "Customary"
    iso4217 = "ISO4217"
    non_si = "Non-SI"
    si = "SI"
    xbrl = "XBRL"


class UnitStatus(enum.Enum):
    """
    Legal values for unit registry entry statuses.  Please note that this is referred to as just
    status (as opposed to unitStatus) in the actual entries but the name has been expanded here
    since status is extremely generic.
    """

    rec = "REC"
    cr = "CR"


class Element(object):
    """Element is used to model a data element within a Taxonomy Concept."""

    def __init__(self):
        """Element constructor."""
        self.abstract = None
        self.id = None
        self.name = None
        self.nillable = None
        self.period_independent = None
        self.substitution_group = None
        self.type_name = None
        self.period_type = None

    def __repr__(self):
        """Return a printable representation of an element."""
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
    """Unit holds the definition of a Unit from the Unit Registry."""

    def __init__(self):
        """Unit constructor."""
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
        """Return a printable representation of a unit."""
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

    def to_dict(self):
        """Convert Unit to dict."""
        return vars(self)

class Taxonomy(object):
    """
    Parent class for Taxonomy.

    Use this to load and access all elements
    of the Taxonomy simultaneously.  Generally speaking this supplies
    a single import location and is better than loading just a portion
    of the Taxonomy unless there is a specific need to save memory.
    """

    def __init__(self):
        """Taxonomy constructor."""
        self.semantic = taxonomy_semantic.TaxonomySemantic()
        self.types = taxonomy_types.TaxonomyTypes()
        self.units = taxonomy_units.TaxonomyUnits()
        self.numeric_types = taxonomy_misc.TaxonomyNumericTypes()
        self.generic_roles = taxonomy_misc.TaxonomyGenericRoles()
        self.ref_parts = taxonomy_misc.TaxonomyRefParts()
        self.documentation = taxonomy_misc.TaxonomyDocstrings()


# Accessor for singleton Taxonomy object:
m_singletonTaxonomy = None

def getTaxonomy():
    """Return the taxonomy."""
    global m_singletonTaxonomy
    if m_singletonTaxonomy is None:
        m_singletonTaxonomy = Taxonomy()
    return m_singletonTaxonomy
