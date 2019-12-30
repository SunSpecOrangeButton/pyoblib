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

import sys
import argparse
from oblib import identifier, ob, taxonomy, validator
from oblib import parser as ob_parser


INFO = """
This the CLI for the Orange Button Core library.  Information is available at the following URL's:

Orange Button Overview: https://sunspec.org/orange-button-initiative/
Orange Button GitHUb: https://github.com/SunSpecOrangeButton
Orange Button pyoblib and CLI GitHub: https://github.com/SunSpecOrangeButton/pyoblib
"""


DASHES = "---------------------------------------------------------------------------------------"


taxonomy = taxonomy.Taxonomy()
csv = False
json = False
xml = False


def info(args):
    print(INFO)


def convert(args):

    p = ob_parser.Parser(taxonomy)

    ff = None
    if json:
        ff = ob_parser.FileFormat.JSON
    elif xml:
        ff = ob_parser.FileFormat.XML
    elif args.infile.lower().endswith(".json") and args.outfile.lower().endswith(".xml"):
        ff = ob_parser.FileFormat.JSON
    elif args.infile.lower().endswith(".xml") and args.outfile.lower().endswith(".json"):
        ff = ob_parser.FileFormat.XML

    if ff is None:
        print("Unable to determine file format.  Conversion not processed.")
        sys.exit(1)

    try:
        p.convert(args.infile, args.outfile, ff, entrypoint_name=args.entrypoint)
    except ob.OBValidationErrors as errors:
        for e in errors.get_errors():
            print(e)


def validate(args):

    p = ob_parser.Parser(taxonomy)

    ff = None
    if json:
        ff = ob_parser.FileFormat.JSON
    elif xml:
        ff = ob_parser.FileFormat.XML
    elif args.infile.lower().endswith(".json"):
        ff = ob_parser.FileFormat.JSON
    elif args.infile.lower().endswith(".xml"):
        ff = ob_parser.FileFormat.XML

    if ff is None:
        print("Unable to determine file format.  Conversion not processed.")
        sys.exit(1)

    try:
        p.validate(args.infile, ff, entrypoint_name=args.entrypoint)
        print("Validation succcessful")
    except ob.OBValidationErrors as errors:
        for e in errors.get_errors():
            print(e)


def generate_identifier(args):
    print(identifier.identifier())


def list_concept_details(args):
    print()
    c = taxonomy.semantic.get_concept_details(args.concept)
    if c is not None:
        print("Id:                ", c.id)
        print("Name:              ", c.name)
        print("Abstract:          ", c.abstract)
        print("Nillable:          ", c.nillable)
        print("Period Independent:", c.period_independent)
        print("Substitution Group:", c.substitution_group.value)
        print("Type:              ", c.type_name)
        print("Typed Domain Ref:  ", c.typed_domain_ref)
        print("Period Type:       ", c.period_type.value)
    else:
        print("Not found")


def list_unit_details(args):
    try:
        unit = taxonomy.units.get_unit(args.unit)
        print("Id:                ", unit.id)
        print("Unit Id:           ", unit.unit_id)
        print("Name:              ", unit.unit_name)
        print("nsUnit:            ", unit.ns_unit)
        print("Item Type:         ", unit.item_type)
        print("Item Type Date:    ", unit.item_type_date)
        print("Symbol:            ", unit.symbol)
        print("Base Standard:     ", unit.base_standard.value)
        print("Definition:        ", unit.definition)
        print("Status:            ", unit.status.value)
        print("Version Date:      ", unit.version_date)
    except ob.OBNotFoundError as error:
        print("Not found")


def list_entrypoints(args):
    for entrypoint in taxonomy.semantic.get_all_entrypoints():
        print(entrypoint)


def list_entrypoints_details(args):

    if csv:
        _, entrypoints_details = taxonomy.semantic.get_all_entrypoints(details=True)

        print("Name, Full Name, Entrypoint Type, Number, Description")
        for e in entrypoints_details:
            d = entrypoints_details[e]
            print('%s, %s, %s, %s, %s' %
            (d.name, d.full_name, d.entrypoint_type.value, d.number, d.description))
    else:
        _, entrypoints_details = taxonomy.semantic.get_all_entrypoints(details=True)

        print('%54s %85s %15s %6s %90s' %
              ("Name", "Full Name", "Entrypoint Type", "Number", "Description"))
        print('%0.54s %0.85s %0.15s %0.6s %0.90s' %
              (DASHES, DASHES, DASHES, DASHES, DASHES))
        for e in entrypoints_details:
            d = entrypoints_details[e]
            print('%54s %85s %15s %6s %90s' %
            (d.name, d.full_name, d.entrypoint_type.value, d.number, d.description))


def list_entrypoint_details(args):

    print()
    e = taxonomy.semantic.get_entrypoint_details(args.entrypoint)
    if e is not None:
        print("Name:            ", e.name)
        print("Full Name:       ", e.full_name)
        print("Entrypoint Type: ", e.entrypoint_type.value)
        print("Number:          ", e.number)
        print("Description:     ", e.description)
    else:
        print("Not found")


def list_entrypoint_concepts_details(args):

    if csv:
        _, concepts_details = taxonomy.semantic.get_entrypoint_concepts(args.entrypoint,
                                                                        details=True)
        print("Id, Name, Abstract, Nillable, Period Indicator, "
              "Substitution Group, Type, Period Type")
        for c in concepts_details:
            d = concepts_details[c]
            print('%s, %s, %s, %s, %s, %s, %s, %s, %s' %
            (d.id, d.name, d.abstract, d.nillable, d.period_independent,
            d.substitution_group.value, d.type_name, d.typed_domain_ref, d.period_type.value))
    else:
        _, concepts_details = taxonomy.semantic.get_entrypoint_concepts(args.entrypoint,
                                                                        details=True)
        print('%85s %80s %8s %8s %10s %20s %28s %8s' %
                ("Id", "Name", "Abstract", "Nillable", "Period Ind",
                 "Substitution Group", "Type", "Period Type"))
        print('%0.85s %0.80s %0.8s %0.8s %0.10s %0.20s %0.28s %0.40s %0.8s' %
                (DASHES, DASHES, DASHES, DASHES, DASHES, DASHES, DASHES, DASHES, DASHES))
        for c in concepts_details:
            d = concepts_details[c]
            print('%85s %80s %8s %8s %10s %20s %28s %40s %8s' %
            (d.id, d.name, d.abstract, d.nillable, d.period_independent,
            d.substitution_group.value, d.type_name, d.typed_domain_ref, d.period_type.value))


def list_concepts(args):
    concepts = taxonomy.semantic.get_entrypoint_concepts(args.entrypoint)
    if concepts is not None:
        for concept in concepts:
            print(concept)
    else:
        print("Not found")


def list_relationships(args):
    relationships = taxonomy.semantic.get_entrypoint_relationships(args.entrypoint)

    if csv:
        print("Role, From, To, Order")
        if relationships is not None:
            for r in relationships:
                print('%s, %s, %s, %s' %
                       (r.role.value, r.from_, r.to, r.order))
    else:
        print('%19s %78s %78s %5s' %
                ("Role", "From", "To", "Order"))
        print('%0.19s %0.78s %0.78s %0.5s' %
                (DASHES, DASHES, DASHES, DASHES))

        if relationships is not None:
            for r in relationships:
                print('%19s %78s %78s %5s' %
                       (r.role.value, r.from_, r.to, r.order))
        else:
            print("Not found")


def list_type_enums(args):
    enums = taxonomy.types.get_type_enum(args.type_name)
    if enums is not None:
        for enum in enums:
            print(enum)
    else:
        print("Not found")


def list_numeric_types(args):
    for numeric_type in taxonomy.numeric_types.get_all_numeric_types():
        print(numeric_type)


def list_ref_parts(args):
    for ref_part in taxonomy.ref_parts.get_all_ref_parts():
        print(ref_part)


def list_generic_roles(args):
    for generic_role in taxonomy.generic_roles.get_all_generic_roles():
        print(generic_role)


def list_units(args):
    for unit in taxonomy.units.get_all_units():
        print(unit)


def list_units_details(args):

    if csv:
        print("Id, Unit ID, Name, nsUnit, Item Type, Item Type Dt, Symbol, Base Std, Status, Ver Dt, Definition")

        for unit_id in taxonomy.units.get_all_units():
            unit = taxonomy.units.get_unit(unit_id)
            print('%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s' %
                   (unit.id, unit.unit_id, unit.unit_name, unit.ns_unit, unit.item_type,
                   unit.item_type_date, unit.symbol, unit.base_standard.value, unit.version_date,
                   unit.status.value, unit.definition))
    else:
        print('%6s %22s %40s %35s %23s %10s %6s %9s %10s %8s %15s' %
              ("Id", "Unit ID", "Name", "nsUnit", "Item Type", "I Type Dt", "Symbol", "Base Std",
               "Status", "Ver Dt", "Definition"))
        print('%0.6s %0.22s %0.40s %0.35s %0.23s %0.10s %0.6s %0.9s %0.10s %0.8s %0.15s' %
                (DASHES, DASHES, DASHES, DASHES, DASHES, DASHES, DASHES, DASHES, DASHES, DASHES, DASHES))

        for unit_id in taxonomy.units.get_all_units():
            unit = taxonomy.units.get_unit(unit_id)
            print('%6s %22s %40s %35s %23s %10s %6s %9s %10s %8s %1s' %
                   (unit.id, unit.unit_id, unit.unit_name, unit.ns_unit, unit.item_type,
                   unit.item_type_date, unit.symbol, unit.base_standard.value, unit.version_date,
                   unit.status.value, unit.definition))


def list_types(args):

    names = taxonomy.semantic.get_all_type_names()
    names.sort()
    for name in names:
        print(name)


def list_concept_documentation(args):
    documentation = taxonomy.documentation.get_concept_documentation(args.concept)
    if documentation is None:
        print("Not Found")
    else:
        print(documentation)


def validate_concept(args):
    print("Valid:", taxonomy.semantic.is_concept(args.concept))


def validate_value(args):
    v = validator.Validator(taxonomy)
    concept_details = taxonomy.semantic.get_concept_details(args.concept)
    if concept_details is None:
        print("Not valid:", args.concept, "is not a concept name.")
        return

    result = v.validate_concept_value(concept_details, args.value)
    if not result[1]:
        print("Valid:", result[0])
    else:
        # Note: the following line is not valid in 2.7 so use sys.stdout.write instead.
        # print("Not valid:", end=" ")
        sys.stdout.write("Not valid: ")
        for error in result[1]:
            print(error)


def validate_entrypoint(args):
    print("Valid:", taxonomy.semantic.is_entrypoint(args.entrypoint))


def validate_identifier(args):
    print("Valid:", identifier.validate(args.identifier))


def validate_type(args):
    print("Valid:", taxonomy.types.is_type(args.type_name))


def validate_numeric_type(args):
    print("Valid:", taxonomy.numeric_types.is_numeric_type(args.numeric_type))


def validate_ref_part(args):
    print("Valid:", taxonomy.ref_parts.is_ref_part(args.ref_part))


def validate_generic_role(args):
    print("Valid:", taxonomy.generic_roles.is_generic_role(args.generic_role))


def validate_unit(args):
    print("Valid:", taxonomy.units.is_unit(args.generic_unit))


def version(args):
    print("Orange Button Core CLI version 0.9.1")


formatter = lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=34)

parent_parser = argparse.ArgumentParser(description='Orange Button Core Library CLI', formatter_class=formatter)
parent_parser.add_argument("--csv", help="place list output in CSV format", action="store_true")
parent_parser.add_argument("--json", help="input format is JSON", action="store_true")
parent_parser.add_argument("--xml", help="input format is XML", action="store_true")
subparsers = parent_parser.add_subparsers(help='commands')

info_parser = subparsers.add_parser('info', help='Information on Orange Button')
info_parser.set_defaults(command='info')

convert_parser = subparsers.add_parser('convert', help='Convert XBRL files from JSON/XML to XML/JSON')
convert_parser.set_defaults(command='convert')
convert_parser.add_argument('infile', action='store', help='The input file')
convert_parser.add_argument('outfile', action='store', help='The output file')
convert_parser.add_argument('--entrypoint', action='store', help='Entrypoint name (will be derived from input if not included)')

validate_parser = subparsers.add_parser('validate', help='Validate XBRL JSON or XML files')
validate_parser.set_defaults(command='validate')
validate_parser.add_argument('infile', action='store', help='The input file')
validate_parser.add_argument('--entrypoint', action='store', help='Entrypoint name (will be derived from input if not included)')

generate_identifier_parser = subparsers.add_parser('generate-identifier',
                                                   help='Generate an Orange Button Identifier')
generate_identifier_parser.set_defaults(command='generate_identifier')

validate_identifier_parser = subparsers.add_parser('validate-identifier',
                                                   help='Validate an Orange Button Identifier')
validate_identifier_parser.set_defaults(command='validate_identifier')
validate_identifier_parser.add_argument('identifier', action='store',
                                        help='The identifier to validate')

version_parser = subparsers.add_parser('version', help='CLI Version')
version_parser.set_defaults(command='version')

taxonomy_parser = subparsers.add_parser('taxonomy', help='Taxonomy Meta-data Related Commands', formatter_class=formatter)
subparsers = taxonomy_parser.add_subparsers(help='commands')

list_concept_details_parser = subparsers.add_parser('list-concept-details',
                                                 help='List Orange Button concept details')
list_concept_details_parser.set_defaults(command='list_concept_details')
list_concept_details_parser.add_argument('concept', action='store',
                                      help='The concept to list details for')

list_unit_details_parser = subparsers.add_parser('list-unit-details',
                                              help='List Orange Button unit details')
list_unit_details_parser.set_defaults(command='list_unit_details')
list_unit_details_parser.add_argument('unit', action='store',
                                   help='The unit to list details for')

list_types_parser = subparsers.add_parser('list-types',
                                              help='List all Orange Button data type names')
list_types_parser.set_defaults(command='list_types')

list_concepts_details_parser = subparsers.add_parser(
        'list-concepts-details',
        help='List concept details in an Orange Button Entry Point')
list_concepts_details_parser.set_defaults(command='list_entrypoint_concepts_details')
list_concepts_details_parser.add_argument('entrypoint', action='store',
                                       help='The entry point to list concepts for')

list_entrypoints_parser = subparsers.add_parser('list-entrypoints', help='List Orange Button Entry Points')
list_entrypoints_parser.set_defaults(command='list_entrypoints')

list_entrypoints_details_parser = subparsers.add_parser('list-entrypoints-details',
                                                        help='List Orange Button Entry Points with details')
list_entrypoints_details_parser.set_defaults(command='list_entrypoints_details')

list_entrypoint_details_parser = subparsers.add_parser('list-entrypoint-details',
                                                 help='List Orange Button entrypoint details')
list_entrypoint_details_parser.set_defaults(command='list_entrypoint_details')
list_entrypoint_details_parser.add_argument('entrypoint', action='store',
                                      help='The entrypoint to list details for')

list_concepts_parser = subparsers.add_parser('list-concepts',
                                             help='List concepts in an Orange Button Entry Point')
list_concepts_parser.set_defaults(command='list_concepts')
list_concepts_parser.add_argument('entrypoint', action='store',
                                  help='The entry point to list concepts for')

list_relationships_parser = subparsers.add_parser('list-relationships',
                                             help='List relationships in an Orange Button Entry Point')
list_relationships_parser.set_defaults(command='list_relationships')
list_relationships_parser.add_argument('entrypoint', action='store',
                                  help='The entry point to list relationships for')

list_types_parser = subparsers.add_parser('list-type-enums',
                                          help='List enumerations in an Orange Button Type')
list_types_parser.set_defaults(command='list_type_enums')
list_types_parser.add_argument('type_name', action='store',
                               help='The type to list enumerations for')

list_numeric_types_parser = subparsers.add_parser('list-numeric-types',
                                                  help='List Orange Button Numeric Types')
list_numeric_types_parser.set_defaults(command='list_numeric_types')

list_ref_parts_parser = subparsers.add_parser('list-ref-parts',
                                              help='List Orange Button Ref Parts')
list_ref_parts_parser.set_defaults(command='list_ref_parts')

list_generic_roles_parser = subparsers.add_parser('list-generic-roles',
                                                  help='List Orange Button Generic Roles')
list_generic_roles_parser.set_defaults(command='list_generic_roles')

list_units_parser = subparsers.add_parser('list-units',
                                          help='List Orange Button Units')
list_units_parser.set_defaults(command='list_units')

list_units_details_parser = subparsers.add_parser(
        'list-units-details',
        help='List Orange Button Units including full details')
list_units_details_parser.set_defaults(command='list_units_details')

list_concept_documentation_parser = subparsers.add_parser('list-concept-documentation',
                                                           help='List Orange Button Documentation for a Concept')
list_concept_documentation_parser.set_defaults(command='list_concept_documentation')
list_concept_documentation_parser.add_argument('concept', action='store',
                                               help='The concept to list documentation for')

validate_concept_parser = subparsers.add_parser('validate-concept',
                                                help='Validate an Orange Button Concept')
validate_concept_parser.set_defaults(command='validate_concept')
validate_concept_parser.add_argument('concept', action='store',
                                     help='The concept to validate')

validate_value_parser = subparsers.add_parser(
        'validate-value',
        help='Validate an Orange Button Concept and its value')
validate_value_parser.set_defaults(command='validate_value')
validate_value_parser.add_argument('concept', action='store',
                                   help='The concept to validate')
validate_value_parser.add_argument('value', action='store',
                                   help='The value to validate')

validate_entrypoint_parser = subparsers.add_parser('validate-entrypoint',
                                           help='Validate an Orange Button Entry Point')
validate_entrypoint_parser.set_defaults(command='validate_entrypoint')
validate_entrypoint_parser.add_argument('entrypoint', action='store',
                                help='The entry point to validate')

validate_type_parser = subparsers.add_parser('validate-type',
                                             help='Validate an Orange Button Type')
validate_type_parser.set_defaults(command='validate_type')
validate_type_parser.add_argument('type_name', action='store',
                                  help='The type to validate')

validate_numeric_type_parser = subparsers.add_parser('validate-numeric-type',
                                                     help='Validate an Orange Button Numeric Type')
validate_numeric_type_parser.set_defaults(command='validate_numeric_type')
validate_numeric_type_parser.add_argument('numeric_type', action='store',
                                          help='The numeric type to validate')

validate_ref_part_parser = subparsers.add_parser('validate-ref-part',
                                                 help='Validate an Orange Button Ref Parts')
validate_ref_part_parser.set_defaults(command='validate_ref_part')
validate_ref_part_parser.add_argument('ref_part', action='store',
                                      help='The Ref Part to validate')

validate_generic_role_parser = subparsers.add_parser('validate-generic-role',
                                                     help='Validate an Orange Button Generic Role')
validate_generic_role_parser.set_defaults(command='validate_generic_role')
validate_generic_role_parser.add_argument('generic_role', action='store',
                                          help='The Generic Role to validate')

validate_unit_parser = subparsers.add_parser('validate-unit',
                                             help='Validate an Orange Button Unit')
validate_unit_parser.set_defaults(command='validate_unit')
validate_unit_parser.add_argument('generic_unit', action='store',
                                  help='The Unit to validate')

args = parent_parser.parse_args()

if args.csv:
    csv = True
if args.json:
    json = True
if args.xml:
    xml = True

if json and xml:
    print("--json and --xml are mutually exclusive.")
    sys.exit(1)

if not hasattr(args, 'command'):
    print('A command must be specified')
    print()
    parent_parser.print_help()
    sys.exit()

globals()[args.command](args)
