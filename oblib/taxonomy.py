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

"""Handles Orange button taxonomy."""

import enum
from oblib import ob


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
        self.typed_domain_ref = None
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
            "," + str(self.typed_domain_ref) + \
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


class TaxonomyNumericTypes(object):
    """
    Represents Miscellaneous Taxonomy Objects.

    Represents objects that are not covered in the
    other classes.  Generally speaking these are rarely used.
    """

    def __init__(self, tl):
        """Misc object constructor."""
        self._numeric_types = tl._load_numeric_types()

    def get_all_numeric_types(self):
        """
        Used to access a list of numeric types.

        Returns:
             list of all numeric types (strings).
        """

        return self._numeric_types

    def is_numeric_type(self, numeric_type):
        """
        Used to check if a numeric type is valid.

        Args:
            numeric_type (string): Numeric type to check for validity.

        Returns:
            True if the numeric type is valid, false otherwise.
        """

        if numeric_type in self._numeric_types:
            return True
        else:
            return False


class TaxonomyGenericRoles(object):
    """
    Represents Generic Roles portion of the taxonomy.  Generally speaking this is rarely used.
    """

    def __init__(self, tl):
        self._generic_roles = tl._load_generic_roles()

    def get_all_generic_roles(self):
        """
        Used to access a list of all generic roles.

        Returns:
             list of all generic roles (strings).
        """
        return self._generic_roles

    def is_generic_role(self, generic_role):
        """
        Used to check if a generic role is valid.

        Args:
            generic_role (string): Generic role to check for validity.

        Returns:
            True if the generic role is valid, false otherwise.
        """
        if generic_role in self._generic_roles:
            return True
        else:
            return False


class TaxonomyRefParts(object):
    """
    Represents the Referential Parts portion of the Taxonomy.  Generally speaking this is rarely used.
    """

    def __init__(self, tl):
        self._ref_parts = tl._load_ref_parts()

    def get_all_ref_parts(self):
        """
        Used to access the a list of all ref parts.

        Returns:
            A list of all ref parts (strings).
        """
        return self._ref_parts

    def is_ref_part(self, ref_part):
        """
        Used to check if a ref part is valid.

        Args:
            ref_part (string): Ref part to check or validity.

        Returns:
            True if the ref part is valid, false otherwise.
        """
        if ref_part in self._ref_parts:
            return True
        else:
            return False


class TaxonomyDocumentation(object):
    """
    Loads the documentation strings for each concept from solar_2018-03-31_r01_lab.xml
    """
    def __init__(self, tl):
        self._documentation = tl._load_documentation()

    def get_all_concepts_documentation(self):
        """
        Used to lookup all docstrings.

        Returns:
            A map of all docstrings with a value of an array of two elements; array element 0 is
            a xlink:label and array element 1 is a xlink:role.
        """
        return self._documentation

    def get_concept_documentation(self, concept):
        """
        Used to load

        Args:
            concept (str): A concept name to lookup.

        Returns:
            The documentation for the concept or None if not found.
        """
        if concept in self._documentation:
            return self._documentation[concept]
        else:
            return None


class TaxonomyTypes(object):
    """
    Represents Taxonomy Types.

    Allows lookup of enumerated values for each Taxonomy Type.

    Please note that in the implementation of this class the variable name
    "type" is never used although "_type" and "types" are in order to avoid
    confusion with the python "type" builtin.
    """

    def __init__(self, tl):
        """Constructor."""
        self._types = tl._load_types()

    def get_all_types(self):
        """
        Used to lookup all types.

        Returns:
             A map and sublists of types.
        """
        return self._types

    def is_type(self, name):
        """
        Validates that a type is in the taxonomy.

        Returns:
            True if the type is present, false otherwise.
        """
        if name in self._types:
            return True
        else:
            return False

    def get_type_enum(self, name):
        """
        Used to lookup a type enumeration.

        Returns:
             An enumeration given a type or None if the type does not exist
             in the taxonomy.
        """
        if name in self._types:
            return self._types[name]
        else:
            return None


class TaxonomyUnits(object):
    """
    Represents Taxonomy Units.

    Allows lookup of units in the taxonomy, and enumerated values for units.
    """

    def __init__(self, tl):
        """Constructor."""
        self._units = tl._load_units()

    def get_all_units(self):
        """
        Used to lookup the entire list of units.

        Returns:
             A dict of units with unit_id as primary key.
        """
        return self._units

    def _by_id(self):
        """Return a dict of the form {id: unit_id}"""
        return {self._units[k].id: k for k in self._units.keys()}

    def _by_unit_name(self):
        """Return a dict of the form {unit_name: unit_id}"""
        return {self._units[k].unit_name: k for k in self._units.keys()}

    def is_unit(self, unit_str, attr=None):
        """
        Returns True if unit_str is the unit_id, unit_name or id of a unit in
        the taxonomy, False otherwise.

        The search for the unit can be restricted by specifying attr as one
        of 'unit_id', 'unit_name', or 'id'.

        Args:
            unit_str: str
                can be unit_id, unit_name or id
            attr: str, default None
                checks only specified attribute, can be 'unit_id', 'unit_name',
                or 'id'

        Returns:
            boolean

        Raises:
            ValueError if attr is not a valid attribute
        """
        if attr=='unit_id':
            return unit_str in self._units.keys()
        elif attr=='unit_name':
            return unit_str in self._by_unit_name().keys()
        elif attr=='id':
            return unit_str in self._by_id().keys()
        elif attr:
            raise ValueError('{} is not a valid unit attribute, must be one of'
                             '"unit_id", "unit_name" or "id"'
                             .format(attr))
        else: # attr is None, check for any attribute
            return (unit_str in self._units.keys() or \
                    unit_str in self._by_id().keys() or \
                    unit_str in self._by_unit_name().keys())

    def get_unit(self, unit_str, attr=None):
        """
        Returns the unit given by unit_str, checking attributes unit_id,
        unit_name and id.

        The search for the unit can be restricted by specifying attr as one
        of 'unit_id', 'unit_name', or 'id'.

        Args:
            unit_str: str
                can be unit_id, unit_name or id
            attr: str, default None
                checks only specified attribute, can be 'unit_id', 'unit_name',
                or 'id'

        Returns:
            unit: dict

        Raises:
            OBNotFoundError if no unit is found.
            ValueError if attr is not unit_id, unit_name, id, or None.
        """
        found = False
        unit = None
        if attr in {'unit_id', 'unit_name', 'id'}:
            # valid attr, search for unit_str in attr's values
            if attr=='unit_id':
                if unit_str in self._units.keys():
                    unit = self._units[unit_str]
                    found = True
            elif attr=='unit_name':
                if unit_str in self._by_unit_name():
                    unit_id = self._by_unit_name()[unit_str]
                    unit = self._units[unit_id]
                    found = True
            elif attr=='id':
                if unit_str in self._by_id():
                    unit_id = self._by_id()[unit_str]
                    unit = self._units[unit_id]
                    found = True
        elif attr:
            raise ValueError('{} is not a recognized unit attribute'
                             .format(attr))
        else:  # attr is None
            # search by unit_id, unit_name or id
            if self.is_unit(unit_str, attr):
                # find unit_id
                try:
                    unit = self._units[unit_str]
                    found = True
                except:
                    if unit_str in self._by_id():
                        unit_id = self._by_id()[unit_str]
                        unit = self._units[unit_id]
                        found = True
                    elif unit_str in self._by_unit_name():
                        unit_id = self._by_unit_name()[unit_str]
                        unit = self._units[unit_id]
                        found = True
        if found:
            return unit
        else:
            raise ob.OBNotFoundError("{} is not the type, name or id of a valid "
                                  "unit".format(unit_str, attr))


class TaxonomySemantic(object):
    """
    Manage semantic portions of the taxonomy including entrypoints, concepts,
    concepts_details, and relationships.
    """

    # Taxonomy data is internally held in three data structures:
    #    - _concept_Details is a map containing all concept details with their id as the key.  This maps to elements
    #      internal to the taxonomy XSD file abd the code that loads this structure uses the term elements to match
    #      the input data.
    #    - _concepts_by_entrypoint is a map containing all concepts for individual entrypoints.  The entrypoint is
    #      the key and the value is a list of all concepts in the entrypoint.
    #    - _relationships_by_entrypoint is a map containing all relationshsips for individual entrypoints.  The
    #      entrypoint is the key and the value is a list of all concepts in the entyrpoint.

    def __init__(self, tl):
        """Constructor."""

        self._concepts_details = tl._load_elements()
        self._concepts_by_entrypoint = tl._load_concepts()
        self._relationships_by_entrypoint = tl._load_relationships()
        self._reduce_unused_semantic_data()

    def _reduce_unused_semantic_data(self):
        """
        During loading of the elements unused elements may be loaded in the
        us-gaap and dei namespaces.  A new elements list can be created that
        does not contain them.  Although there is no other known cases of
        unused memory if any are found they should be addressed.

        Removing the elements has two benefits:
            - Allows simplifcation of accessor methods which no longer have to filter unused data.
            - Reduces in-memory footprint of data
        """
        # Create a list of elements in use and set them all to False
        concept_details_in_use = {}
        for e in self._concepts_details:
            concept_details_in_use[e] = False

        # Find all elements loaded by the taxonomy in the concepts object and
        # set them to True
        for key in self._concepts_by_entrypoint:
            for c in self._concepts_by_entrypoint[key]:
                concept_details_in_use[c] = True

        # Create a new elements list and only add the elements that are in use.
        ne = {}
        for e in self._concepts_details:
            if concept_details_in_use[e]:
                ne[e] = self._concepts_details[e]
        self._concepts_details = ne

    def get_all_concepts(self, details=False):
        """
        Return all concepts in the taxonomy.

        Args:
            details : boolean, default False

        Returns:
            list of concept names if details=False
            dict of concept details if details=True
        """
        if not details:
            return list(self._concepts_by_entrypoint)
        else:
            return self._concepts_details

    def get_all_type_names(self):
        """
        Used to access all type names in elements of the taxonomy.

        Returns:
             list of type names (strings).
        """
        type_names = set()  # use set to eliminate duplicates
        for e in self._concepts_details:
            type_names.add(self._concepts_details[e].type_name)
        return list(type_names)

    def is_concept(self, concept):
        """
        Validate if a concept is present in the Taxonomy.

        Args:
            concept (string): Concept id with the namespace required.

        Return:
            True if concept is present, False otherwise.
        """

        if concept in self._concepts_details:
            return True
        else:
            return False

    def is_entrypoint(self, entrypoint):
        """
        Validate if an entrypoint type is present in the Taxonomy.

        Args:
            entrypoint (string): Entrypoint name to check for presence.

        Return:
            True if the entrypoint is present, False otherwise.
        """
        if entrypoint in self._concepts_by_entrypoint:
            return True
        else:
            return False

    def get_entrypoint_concepts(self, entrypoint, details=False):
        """
        Return a list of all concepts in the entrypoint, with concept details
        (optional).

        Args:
            entrypoint: str
                name of the entrypoint
            details: boolean, default False
                if True return details for each concept

        Returns:
            concepts: list
                elements of the list are concept names
            details: dict
                primary key is name from concepts, value is dict of concept
                details
        """
        concepts = []
        if entrypoint in self._concepts_by_entrypoint:
            concepts = self._concepts_by_entrypoint[entrypoint]
            if details:
                ci = {}
                for concept in concepts:
                    if concept in self._concepts_details:
                        ci[concept] = self._concepts_details[concept]
                    else:
                        # NOTE: This is encountered if a historical bug in the Taxonomy occurs.
                        # Printing a warning will be left in case this reoccurs in the future.
                        print("Warning, concept not found:", concept)

                return concepts, ci
        return concepts

    def get_entrypoint_relationships(self, entrypoint):
        """
        Used to find the relationships for an entrypoint.

        Args:
            Entrypoint (string): Entrypoint name to lookup relationships for.

        Returns:
             A list of all relationships in an entry point.  Iif the concept exists but has no
             relationships an empty list is returned.
        """

        if entrypoint in self._concepts_by_entrypoint:
            if entrypoint in self._relationships_by_entrypoint:
                return self._relationships_by_entrypoint[entrypoint]
            else:
                return []
        else:
            return None

    def get_all_entrypoints(self):
        """
        Used to access  a list of all entry points (data, documents, and processes) in the Taxonomy.

        Returns:
            A list of entrypoint names (strings).
        """

        return list(self._concepts_by_entrypoint)

    def get_concept_details(self, concept):
        """
        Return information on a single concept.

        Args:
            concept : str
                concept name

        Returns:
            dict containing concept attributes

        Raises:
            KeyError if concept is not found
        """
        if self.is_concept(concept):
            return self._concepts_details[concept]
        else:
            raise KeyError('{} is not a concept in the taxonomy'.format(concept))
            return None


class Taxonomy(object):
    """
    Parent class for Taxonomy.

    Use this class to load and access all elements of the Taxonomy. Taxonomy
    supplies a single import location and is better than loading a portion
    of the Taxonomy unless there is a specific need to save memory.
    """

    def __init__(self):
        """Taxonomy constructor."""

        from oblib import taxonomy_loader
        tl = taxonomy_loader.TaxonomyLoader()

        self.semantic = TaxonomySemantic(tl)
        self.types = TaxonomyTypes(tl)
        self.units = TaxonomyUnits(tl)
        self.numeric_types = TaxonomyNumericTypes(tl)
        self.generic_roles = TaxonomyGenericRoles(tl)
        self.ref_parts = TaxonomyRefParts(tl)
        self.documentation = TaxonomyDocumentation(tl)
