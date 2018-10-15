# Licensed under the Apache License, Version 2.0 (the "License");
# pyou may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import argparse

import identifier

INFO = """
This the CLI for the Orange Button Core libary.  Information is available at the following URL's:

Orange Button Overview: https://sunspec.org/orange-button-initiative/
Orange Button GitHUb: https://github.com/SunSpecOrangeButton
Orange Button CLI GitHub: https://github.com/SunSpecOrangeButton/core
"""

def info(args):
    print(INFO)

def generate_identifier(args):
    print(identifier.identifier())

def validate_identifier(args):
    print("Valid:", identifier.validate(args.identifier))

def version(args):
    print("Orange Button Core CLI version 0.0.1")

parser = argparse.ArgumentParser(description='Orange Button Core Library CLI')
subparsers = parser.add_subparsers(help='commands')

info_parser = subparsers.add_parser('info', help='Information on Orange Button')
info_parser.set_defaults(command='info')

generate_identifier_parser = subparsers.add_parser('generate-identifier', help='Generate an Orange Button Identifier')
generate_identifier_parser.set_defaults(command='generate_identifier')

validate_identifier_parser = subparsers.add_parser('validate-identifier', help='Validate an Orange Button Identifier')
validate_identifier_parser.set_defaults(command='validate_identifier')
validate_identifier_parser.add_argument('identifier', action='store', help='The identifer to validate')

version_parser = subparsers.add_parser('version', help='CLI Version')
version_parser.set_defaults(command='version')

args = parser.parse_args()

if not hasattr(args, 'command'):
    print('A command must be specified')
    print()
    parser.print_help()
    sys.exit()
 
globals()[args.command](args)
