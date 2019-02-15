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

"""Handles Orange button taxonomy."""

import enum
from oblib import taxonomy_types, taxonomy_misc


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
    Legal values for unit registry entry status.  Please note that UnitStatus
    is referred to as just status in the actual entries. The name has been
    expanded here since status is generic.
    """

    rec = "REC"
    cr = "CR"


class RelationshipRole(enum.Enum):
    """
    Legal values for Relationship roles.
    """

    dimension_all = "all"
    dimension_default = "dimension-default"
    dimension_domain = "dimension-domain"
    domain_member = "domain-member"
    hypercube_dimension = "hypercube-dimension"


class ConceptDetails(object):
    """
    ConceptDetails models a data element within a Taxonomy Concept.

    Attributes:
        abstract: boolean
            False for standard concepts, True for concepts that
            model relationships but don't hold data.
        id: str
            ID with the namespace (solar:, us-gaap:, dei:) for the concept.
        name: str
            Name of the concept, usually identical to the ID without
            the namespace.
        nillable: boolean
            True if the concept can be set to None, False if it
            must have a value set.
        period_independent: boolean
            True if the concept is period independent, false otherwise.
        substitution_group: SubstitutionGroup
            The type of substitution group.
        type_name: str
            XBRL data type.
        period_type: PeriodType
            Duration if the period models a period of time (including forever),
            instance if it is a point in time.
    """

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


class Relationship(object):
    """
    Relationship holds a taxonomy relationship record.

    Attributes:
        role: str
            XBRL Arcrole
        from_: str
            Models a relationship between two concepts in
            conjunction with to.
        to: str
            Models a relationship between two concpets in conjunction
            with from_.
        order: int
            The order of the relationshps for a single entrypoint.
    """

    def __init__(self):
        """Relationship constructor."""
        self.role = None
        self.from_ = None
        self.to = None
        self.order = None

    def __repr__(self):
        """Return a printable representation of an relationship."""
        return "{" + str(self.role) + \
            "," + str(self.from_) + \
            "," + str(self.to) + \
            "," + str(self.order) + \
            "}"


class Unit(object):
    """
    Unit holds the definition of a Unit from the Unit Registry.

    Attributes:
        id: str
            ID for this unit (sample is u00020), not normally used
            but preserved for completeness.
        unit_id: str
            Unit ID for this unit (for example MMBoe), usually
            the main lookup value.
        unit_name: str
            Spells out Unit ID (for example MMBoe == Millions 
            of Barrels of Oil Equivalent)
        ns_unit: str
            Namespace, not normally used in processing.
        item_type: str
            XBRL item type associated with the unit.
        item_type_date: datetime.datetime
            Date the item type was set.
        symbol: str
            Symbol used on presentation - may be same as unit_id.
        definition: str
            Definition of unit, may be same as name or may 
            elaborate.
        base_standard: BaseStandard
            Base standard for a unit.
        status: UnitStatus
            Unit status for a unit.
        version_date: datetime.datetime
            Date for a unit
    """

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

    Use this class to load and access all elements of the Taxonomy. Taxonomy
    supplies a single import location and is better than loading a portion
    of the Taxonomy unless there is a specific need to save memory.
    """

    def __init__(self):
        """Taxonomy constructor."""

        # Temporary fix for the circular dependency issue
        from oblib import taxonomy_semantic, taxonomy_units

        self.semantic = taxonomy_semantic.TaxonomySemantic()
        self.types = taxonomy_types.TaxonomyTypes()
        self.units = taxonomy_units.TaxonomyUnits()
        self.numeric_types = taxonomy_misc.TaxonomyNumericTypes()
        self.generic_roles = taxonomy_misc.TaxonomyGenericRoles()
        self.ref_parts = taxonomy_misc.TaxonomyRefParts()
        self.documentation = taxonomy_misc.TaxonomyDocumentation()


# Accessor for singleton Taxonomy object:
m_singletonTaxonomy = None


def getTaxonomy():
    """Return the taxonomy."""
    global m_singletonTaxonomy
    if m_singletonTaxonomy is None:
        m_singletonTaxonomy = Taxonomy()
    return m_singletonTaxonomy
