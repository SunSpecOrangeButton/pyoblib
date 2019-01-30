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

"""Validation functions."""

import identifier
import re
import sys
import taxonomy
import validators
from datetime import date
from datetime import datetime

BOOLEAN_TRUE = ['true', 't', 'y', '1']
BOOLEAN_FALSE = ['false', 'f', 'n', '0']
BOOLEAN_VALUES = BOOLEAN_TRUE + BOOLEAN_FALSE

# TODO: There are several main improvements at this point in time:
#
#  1) Currently Python types (int, bool, str) are supported for values.
#     However there is a second case where the inputs are always strings.
#     For instance the string "37" would be valid for xbrli:integerItemType
#     while "Arf" would not be.
#  2) There is a much larger number of  basic xbrli types that should be
#     included beyond boolean, string, and integer.
#  3) XBRL types that are derived from the basic types should also be
#     implemented.  This will require the entire Taxonomy class (not just
#     the stripped down Taxonomy class shipped in the ZIP file).
#  4) In all likelihood end users will wish to receive more information on
#     what caused the error condition as opposed to simply receiving False.
#     This may require a different function signature.


def validate_concept_value(concept, value):
    """Validate a concept."""
    errors = []
    result = value, []
    # If null check if nillable is ok and return
    if value is None and not concept.nillable:
        errors += ["'{}' is not allowed to be nillable (null).".format(concept.id)]
    enum = taxonomy.getTaxonomy().types.get_type_enum(concept.type_name)
    is_enum = enum is not None
    # Check data type and validator calling
    if type(concept.type_name).__name__ in ["str", "unicode"]:
        method_name = _get_validator_method_name(concept.type_name)
        validator_module = sys.modules[__name__]
        found_method = getattr(validator_module, method_name, None)
        if found_method is not None:
            if is_enum:
                result = found_method(value, enum)
            else:
                result = found_method(value)
        elif is_enum:
            result = _generic_enum_validator(value, concept, enum)
        else:
            raise Exception("Concept '{}' could not be processed. Missing method '{}'.".format(concept.type_name, method_name))

    # Check identifiers.  This is based upon the name of the field containing
    # the word Identifier in it.
    if concept.id.find("Identifier") != -1:
        if identifier.validate(value) is False:
            errors += ["'{}' is not valid identifier.".format(concept.id)]

    # If all conditions clear then the value passes.
    errors += result[1]
    return result[0], errors


def _get_validator_method_name(type_name):
    """Return the validator for a type."""
    # Check if type nillable and not string
    if type_name is None and type(type_name) is not str:
        return type_name

    type_name = re.sub("[^0-9a-zA-Z]", "_", type_name)
    type_name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", type_name)
    type_name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", type_name).lower()
    return "_" + type_name + "_validator"

def _generic_enum_validator(value, concept, enum):
    errors = []
    if (value not in enum):
        errors.append("Value '{}' is not found in enum list for type '{}'."
                      .format(value, concept.type_name))
    return value, errors

# validators implementation
# TODO: could be moved to other file and loaded and even loading custom
# validator files

def _xbrli_boolean_item_type_validator(value):
    """Returns python boolean if value can be converted"""
    errors = []
    if value is True:
        pass
    elif value is False:
        pass
    else:
        # value is not a boolean
        if str(value).lower() in BOOLEAN_VALUES:
            value = str(value).lower() in BOOLEAN_TRUE
        else:
            errors.append("'{}' is not a valid boolean value.".format(value))
    return value, errors


def _xbrli_string_item_type_validator(value):
    """Returns python str if value can be converted"""
    errors = []
    try:
        value = str(value)
    except:
#        if type(value).__name__ not in ["str", "unicode"]:
        errors.append("'{}' is not a valid string value.".format(value))
    return value, errors


def _xbrli_integer_item_type_validator(value):
    """Returns python int if value can be converted"""
    errors = []
    if isinstance(value, int):
        value = int(value)
    elif isinstance(value, str):
        try:
            value = int(value)
        except:
            errors.append("'{}' is not a valid integer value.".format(value))
    else:
        errors.append("'{}' is not a valid integer value.".format(value))
    return value, errors


def _xbrli_decimal_item_type_validator(value):
    """XBRLI decimal validator."""
    errors = []
    if type(value) is str:
        try:
            result = float(value)
        except ValueError as ex:
            errors += ["'{}' is not a valid decimal value.".format(value)]
    elif type(value) is not int:
        errors += ["'{}' is not a valid decimal value.".format(value)]
    return value, errors

def _xbrli_monetary_item_type_validator(value):
    """XBRLI monetary validator."""
    errors = []
    if type(value) is str:
        try:
            result = float(value)
        except ValueError as ex:
            errors += ["'{}' is not a valid monetary value.".format(value)]
    elif type(value) is not int:
        errors += ["'{}' is not a valid monetary value.".format(value)]
    return value, errors

def _xbrli_date_item_type_validator(value):
    """XBRLI date validator."""
    errors = []
    if type(value) is str:
        try:
            result = datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError as ex:
            print(ex)
            errors += ["'{}' is not a valid date value.".format(value)]
    elif type(value) is not date:
        print("{} is not {}".format(type(value), type(date)))
        errors += ["'{}' is not a valid date value.".format(value)]
    return value, errors

def _solar_document_identifier_appraisal(value):
    """SOLAR Document Identifier Appraisal validator"""
    return _xbrli_boolean_item_type_validator(value)

def _xbrli_duration_item_type_validator(value):
    """XBRLI duration validator."""
    return _xbrli_integer_item_type_validator(value)

def _num_power_item_type_validator(value):
    """NUM power validator."""
    return _xbrli_decimal_item_type_validator(value)

def _num_percent_item_type_validator(value):
    """NUM percent validator."""
    return _xbrli_decimal_item_type_validator(value)

def _dei_legal_entity_identifier_item_type_validator(value):
    """DEI Legal Entity Identifier"""
    return _xbrli_string_item_type_validator(value)

def _xbrli_any_uri_item_type_validator(value):
    """XBRLI Any URI validator"""
    errors = []
    result = _xbrli_string_item_type_validator(value)
    if not validators.url(value):
        errors += "'{}' is invalid URI"
    errors += result[1]
    return result[0], errors

def _num_us_electric_current_item_type_validator(value):
    """NUM US Electric Current validator"""
    return _xbrli_decimal_item_type_validator(value)

def _num_us_frequency_item_type_validator(value):
    """NUM US Frequency validator"""
    return _xbrli_decimal_item_type_validator(value)

def _num_us_insolation_item_type_validator(value):
    """NUM US Insolation validator"""
    return _xbrli_decimal_item_type_validator(value)

def _num_us_irradiance_item_type_validator(value):
    """NUM US Irradience validator"""
    return _xbrli_decimal_item_type_validator(value)

def _num_us_plane_angle_item_type_validator(value):
    """NUM US Plane Angle validator"""
    return _xbrli_decimal_item_type_validator(value)

def _num_us_pressure_item_type_validator(value):
    """NUM US Pressure validator"""
    return _xbrli_decimal_item_type_validator(value)

def _num_us_speed_item_type_validator(value):
    """NUM US Speed validator"""
    return _xbrli_decimal_item_type_validator(value)

def _num_us_temperature_item_type_validator(value):
    """NUM US Temperature validator"""
    return _xbrli_decimal_item_type_validator(value)

def _num_us_voltage_item_type_validator(value):
    """NUM US Voltage validator"""
    return _xbrli_decimal_item_type_validator(value)

def _num_area_item_type_validator(value):
    """NUM Area validator"""
    return _xbrli_decimal_item_type_validator(value)

def _num_energy_item_type_validator(value):
    """NUM Energy validator"""
    return _xbrli_decimal_item_type_validator(value)

def _num_length_item_type_validator(value):
    """NUM Length validator"""
    return _xbrli_decimal_item_type_validator(value)

def _num_mass_item_type_validator(value):
    """NUM Mass validator"""
    return _xbrli_decimal_item_type_validator(value)

def _num_volume_item_type_validator(value):
    """NUM Volume validator"""
    return _xbrli_decimal_item_type_validator(value)

