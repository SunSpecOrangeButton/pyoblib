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

import identifier
import re
import sys

# TODO: There are several main improvements at this point in time:
#
#  1) Currently Python types (int, bool, str) are supported for values.
#     However there is a second case where the inputs are always strings.
#     For instance the string "37" would be valid for xbrli:integerItemType
#     whie "Arf" woudld not be.
#  2) There is a much larger number of  basic xbrli types that should be
#     included beyond boolean, string, and integer.
#  3) XBRL types that are derived from the basic types should also be
#     implmented.  This will require the entire Taxonomy class (not just
#     the stripped down Taxonomy class shipped in the ZIP file).
#  4) In all likelihood end users will wish to receive more information on
#     what caused the error condition as opposed to simply receiving False.
#     This may require a different function signature.

def validate_concept_value(concept, value):

    errors = []
    # If null check if nillable is ok and return
    if value is None and not concept.nillable:
        errors += ["'{}' is not allowed to be nillable (null).".format(concept.id)]

    # Check data type and validator calling
    if type(concept.type_name) is str:
        method_name = get_validator_method_name(concept.type_name)
        validator_module = sys.modules[__name__]
        found_method = getattr(validator_module, method_name, None)
        if found_method is not None:
            errors += found_method(value, concept)

    # Check identifiers.  This is based upon the name of the field containing the word Identifier
    # in it.
    if concept.id.find("Identifier") != -1:
        return identifier.validate(value)

    # If all conditions clear then the value passes.
    return errors


def get_validator_method_name(type_name):

    # Check if type nillable and not string
    if type_name is None and type(type_name) is not str:
        return type_name

    type_name = re.sub("[^0-9a-zA-Z]", "_", type_name)
    type_name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", type_name)
    type_name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", type_name).lower()
    return type_name + "_validator"


# validators implementation
# TODO: could be moved to other file and loaded and even loading custom validator files

def xbrli_boolean_item_type_validator(value, concept):
    errors = []
    if type(value) is str:
        if value.lower() not in ['true', 'false']:
            errors += ["'{}' is not a valid boolean value.".format(value)]
    elif type(value) is not bool:
        errors += ["'{}' is not a valid boolean value.".format(value)]
    return errors


def xbrli_string_item_type_validator(value, concept):
    errors = []
    if type(value) is not str:
        errors += ["'{}' is not a valid string value.".format(value)]
    return errors


def xbrli_integer_item_type_validator(value, concept):
    errors = []
    if type(value) is str:
        try:
            result = int(value)
        except ValueError as ex:
            errors += ["'{}' is not a valid integer value.".format(value)]
    elif type(value) is not int:
        errors += ["'{}' is not a valid integer value.".format(value)]
    return errors