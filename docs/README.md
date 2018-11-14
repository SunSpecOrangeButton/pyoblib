Overview
-----------------

Currently the source code contains:

* Identifier
* Taxonomy

Identifier Design
-----------------
Identifier is a single module that allows generation and validation of Orange Button Identifiers (currently UUID's).

Taxonomy Design
-----------------
Taxonomy returns an in memory representation of the Solar Taxonomy XSD (available at [solar-taxonomy](https://github.com/SunSpecOrangeButton/solar-taxonomy)

![
](Taxonomy.png)

Usage
-----------------
<<<<<<< HEAD
A series of shell scripts are availalable to assist with development, packaging, etc....   Their state is preliminary but they can be used to get started.
=======
A series of shell scripts are available to assist with development, packaging, etc....   Their state is preliminary but they can be used to get started.
>>>>>>> ad5f7d49e070dd592f86afcf2c21222ef9894d12

* cli.sh: Runs the CLI before it is packaged.
* dist-cli.sh: Packages the CLI into a single file executable.
* docs.sh: Creates the documentation (currently requires some manual work).
* setup-dev.sh: Downloads the solar-taxonomy, us-gaap taxonomy, and Units registry.
* tests-cli.sh Runs the CLI test suite.
* tests.sh Runs the python tests.

All scripts must be run from the root core directory (i.e. "scripts/tests.sh" is the correct usage).  Run "scripts/setup-dev.sh" before usage of other scripts.

API
-----------------

Module identifier
-----------------

Variables
---------
REG_EX

Functions
---------
identifier()
    Returns valid UUID for Orange Button identifiers

validate(inp)
    Validates that a particular string is either a valid UUID or not a valid UUID.


Module taxonomy
---------------

Variables
---------
SOLAR_TAXONOMY_DIR

Classes
-------
Element 
    Element is used to model a data element within a Taxonomy Concept.

    Ancestors (in MRO)
    ------------------
    taxonomy.Element
    __builtin__.object

    Instance variables
    ------------------
    abstract

    id

    name

    nillable

    period_independent

    period_type

    substitution_group

    type_name

    Methods
    -------
    __init__(self)

Taxonomy 
    Parent class for Taxonomy.  Use this to load and access all elements
    of the Taxonomy simultaneously.  Generally speaking this supplies
    a single import location and is better than loading just a portion
    of the Taxonomy unless there is a specific need to save memory.

    Ancestors (in MRO)
    ------------------
    taxonomy.Taxonomy
    __builtin__.object

    Instance variables
    ------------------
    misc

    semantic

    types

    units

    Methods
    -------
    __init__(self)

Unit 
    Unit holds the definition of a Unit from the Unit Registry.

    Ancestors (in MRO)
    ------------------
    taxonomy.Unit
    __builtin__.object

    Instance variables
    ------------------
    base_standard

    definition

    id

    item_type

    item_type_date

    ns_unit

    status

    symbol

    unit_id

    unit_name

    version_date

    Methods
    -------
    __init__(self)


Module taxonomy_semantic
------------------------

Classes
-------
TaxonomySemantic 
    Ancestors (in MRO)
    ------------------
    taxonomy_semantic.TaxonomySemantic
    __builtin__.object

    Methods
    -------
    __init__(self)

    concept_info(self, concept)
        Returns information on a single concept.

    concepts_ep(self, data)
        Returns a list of all concepts in an end point

    concepts_info_ep(self, data)
        Returns a list of all concepts and their attributes in an end point

    elements(self)
        Returns a map of elements.

    validate_concept(self, concept)
        Validates if a concept is present in the Taxonomy

    validate_concept_value(self, concept, value)
        Validates if a concept is present in the Taxonomy and that its value is legal.

    validate_ep(self, data)
        Validates if an end point type is present in the Taxonomy


Module taxonomy_types
---------------------

Classes
-------
TaxonomyTypes 
    Represents Taxonomy Types and allows lookup of enumerated values for each Taxonomy Type.

    Plese note that in the implementation of this class the variable name "type" is never
    used although "_type" and "types" are in order to avoid confusion with the python
    "type" builtin.

    Ancestors (in MRO)
    ------------------
    taxonomy_types.TaxonomyTypes
    __builtin__.object

    Methods
    -------
    __init__(self)

    type_enum(self, type_name)
        Returns an enumeration given a type or None if the type does not exist in the taxonomy.

    types(self)
        Returns a map and sublists of all types.

    validate_type(self, type_name)
        Validates that a type is in the taxonomy.


Module taxonomy_units
---------------------

Classes
-------
TaxonomyUnits 
    Represents Taxonomy Units and allows lookup of enumerated values for each Taxonomy Unit.

    Ancestors (in MRO)
    ------------------
    taxonomy_units.TaxonomyUnits
    __builtin__.object

    Methods
    -------
    __init__(self)

    unit(self, unit_id)
        Returns an unit given a unit_id or None if the type does not exist in the taxonomy.

    units(self)
        Returns a map and sublists of all units.

    validate_unit(self, unit_id)
        Validates that a unit is in the taxonomy based on its id.


Module taxonomy_misc
--------------------

Classes
-------
TaxonomyMisc 
    Represents Miscellaneous Taxonomy Objects that is not covered in the
    other classes.  Generally speaking these are rarely used.

    Ancestors (in MRO)
    ------------------
    taxonomy_misc.TaxonomyMisc
    __builtin__.object

    Methods
    -------
    __init__(self)

    generic_roles(self)
        A list of genericroles

    numeric_types(self)
        A list of numeric types.

    ref_parts(self)
        A list of ref parts.

    validate_generic_role(self, generic_role)
        Check if a generic role is valid.

    validate_numeric_type(self, numeric_type)
        Check if a numeric type is valid.

    validate_ref_part(self, ref_part)
        Check if a ref part is valid.

