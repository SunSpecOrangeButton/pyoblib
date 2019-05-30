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

"""Validation functions."""

import re
from datetime import date, datetime
from oblib import identifier, ob
import validators


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


class Validator(object):
    """
    Validates values for concepts.

    Args:
        taxonomy (Taxonomy): initialized Taxonomy.
    """

    def __init__(self, taxonomy):
        """ Initializes Validator """
        self._taxonomy = taxonomy

    def validate_concept_value(self, concept_details, value):
        """
        Validate a concept value.

        Args:
            concept_details (ConceptDetails): concept details.
            value (*): value to be validated.

        Returns:
            A tuple (*, list of str) containing original or converted value 
            and list of errors (can be empty).
        """
        errors = []
        result = (value, [])
        # If null check if nillable is ok and return
        if value is None and not concept_details.nillable:
            errors += ["'{}' is not allowed to be nillable (null)."
                       .format(concept_details.id)]
        enum = self._taxonomy.types.get_type_enum(concept_details.type_name)
        # Check data type and validator calling
        if type(concept_details.type_name).__name__ in ["str", "unicode"]:
            method_name = self._get_validator_method_name(concept_details.type_name)
            # validator_module = sys.modules[__name__]
            found_method = getattr(self, method_name, None)
            if found_method:
                if enum:
                    result = found_method(value, enum)
                else:
                    result = found_method(value)
            elif enum:
                result = self._generic_enum_validator(value, concept_details,
                                                      enum)
            else:
                raise ob.OBValidationError(
                    "Concept '{}' could not be processed. Missing method '{}'."
                    .format(concept_details.type_name, method_name))

        # Check identifiers.  This is based upon the name of the field containing
        # the word Identifier in it.  Avoid UtilityIdentifier which is a LEI.
        if concept_details.id != "solar:UtilityIdentifier" and concept_details.id.find("Identifier") != -1:
            if not identifier.validate(value):
                errors += ["'{}' is not valid identifier.".format(concept_details.id)]

        # If all conditions clear then the value passes.
        errors += result[1]
        return result[0], errors

    def _get_validator_method_name(self, type_name):
        """
        Return the validator function name for a type.

        Args:
            type_name (str): Name of the type

        Returns:
            Internal function name as string
        """
        # Check if type nillable and not string
        if type_name is None and type(type_name) is not str:
            return type_name

        type_name = re.sub("[^0-9a-zA-Z]", "_", type_name)
        type_name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", type_name)
        type_name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", type_name).lower()
        return "_" + type_name + "_validator"

    def _generic_enum_validator(self, value, concept_details, enum):
        """
        A generic validator for concept enum value.

        Args:
            value (str): value representing enum value
            concept_details (ConceptDetails): concept details
            enum (list of str): enumerator of all possible values

        Returns:
            A Tuple (str, list of str) containing original and list of errors (if any)
        """
        errors = []
        if (value not in enum):
            errors.append("Value '{}' is not found in enum list for type '{}'."
                          .format(value, concept_details.type_name))
        return value, errors

    # validators implementation
    # TODO: could be moved to other file and loaded and even loading custom
    # validator files

    def _xbrli_boolean_item_type_validator(self, value):
        """
        A validator for XBRLI boolean item type.

        Args:
            value (boolean or int or str): value to be validated and converted
            if needed.

        Returns:
            A Tuple (boolean, list of str) containing original or converted
            value and list of errors (can be empty).
        """
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

    def _xbrli_string_item_type_validator(self, value):
        """
        A validator for XBRLI string item type.

        Args:
            value (*): value to be validated and converted if needed.

        Returns:
            A Tuple (str, list of str) containing original or converted value
            and list of errors (can be empty).
        """
        errors = []
        try:
            value = str(value)
        except:
            #        if type(value).__name__ not in ["str", "unicode"]:
            errors.append("'{}' is not a valid string value.".format(value))
        return value, errors

    def _xbrli_integer_item_type_validator(self, value):
        """
        A validator for XBRLI integer item type.

        Args:
            value (int or decimal or str): value to be validated and 
            converted if needed.

        Returns:
            A Tuple (int, list of str) containing original or converted value
            and list of errors (can be empty).
        """
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

    def _xbrli_decimal_item_type_validator(self, value):
        """
        A validator for XBRLI decimal item type.

        Args:
            value (decimal or int or str): value to be validated and converted
            if needed.

        Returns:
            A Tuple (float, list of str) containing original or converted value
            and list of errors (can be empty).
        """
        errors = []
        if type(value) is str:
            try:
                value = float(value)
            except ValueError as ex:
                errors += ["'{}' is not a valid decimal value.".format(value)]
        elif type(value) is not int:
            errors += ["'{}' is not a valid decimal value.".format(value)]
        return value, errors

    def _xbrli_monetary_item_type_validator(self, value):
        """
        A validator for XBRLI monetary item type.

        Args:
            value (decimal or int or str): value to be validated and converted
            if needed.

        Returns:
            A Tuple (float, list of str) containing original or converted value
            and list of errors (can be empty).
        """
        errors = []
        if type(value) is str:
            try:
                value = float(value)
            except ValueError as ex:
                errors += ["'{}' is not a valid monetary value.".format(value)]
        elif type(value) is not int:
            errors += ["'{}' is not a valid monetary value.".format(value)]
        return value, errors

    def _xbrli_date_item_type_validator(self, value):
        """
        A validator for XBRLI date item type.

        Args:
            value (date or str): value to be validated and converted if needed.

        Returns:
            A Tuple (date, list of str) containing original or
            converted value and list of errors (can be empty).
        """
        errors = []
        if type(value) is str:
            try:
                value = datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError as ex:
                # print(ex)
                errors += ["'{}' is not a valid date value.".format(value)]
        elif type(value) is not date:
            print("{} is not {}".format(type(value), type(date)))
            errors += ["'{}' is not a valid date value.".format(value)]
        return value, errors

    def _solar_document_identifier_appraisal(self, value):
        """
            A validator for SOLAR Document Identifier Appraisal concept.

            Args:
                value (boolean or str): value to be validated and converted if needed

            Returns:
                A Tuple (boolean or str, list of str) containing original or converted value and list of errors (if any)
        """
        return self._xbrli_boolean_item_type_validator(value)

    def _xbrli_duration_item_type_validator(self, value):
        """
            A validator for XBRLI duration concept.

            Args:
                value (int or str): value to be validated and converted if needed

            Returns:
                A Tuple (int or str, list of str) containing original or converted value and list of errors (if any)
        """
        return self._xbrli_integer_item_type_validator(value)

    def _num_power_item_type_validator(self, value):
        """
            A validator for NUM power concept.

            Args:
                value (decimal or int or str): value to be validated and converted if needed

            Returns:
                A Tuple (decimal or int or str, list of str) containing original
                or converted value and list of errors (if any)
        """
        return self._xbrli_decimal_item_type_validator(value)

    def _num_percent_item_type_validator(self, value):
        """
            A validator for NUM percent concept.

            Args:
                value (decimal or int or str): value to be validated and converted if needed

            Returns:
                A Tuple (decimal or int or str, list of str) containing original or converted value
                and list of errors (if any)
        """
        return self._xbrli_decimal_item_type_validator(value)

    def _dei_legal_entity_identifier_item_type_validator(self, value):
        """
            A validator for DEI Legal Entity Identifier concept.

            Args:
                value (str or int): value to be validated and converted if needed

            Returns:
                A Tuple (str or int, list of str) containing original or converted value and list of errors (if any)
        """
        return self._xbrli_string_item_type_validator(value)

    def _xbrli_any_uri_item_type_validator(self, value):
        """
            A validator for XBRLI Any URI concept.

            Args:
                value (str): value to be validated and converted if needed

            Returns:
                A Tuple (str, list of str) containing original or converted value
                and list of errors (if any)
        """

        errors = []
        result = self._xbrli_string_item_type_validator(value)
        if not validators.url(value):
            errors += "'{}' is invalid URI"
        errors += result[1]
        return result[0], errors

    def _num_us_electric_current_item_type_validator(self, value):
        """
            A validator for NUM US Electric Current concept.

            Args:
                value (decimal or int or str): value to be validated and converted if needed

            Returns:
                A Tuple (decimal or int or str, list of str) containing original or converted value
                and list of errors (if any)
        """
        return self._xbrli_decimal_item_type_validator(value)

    def _num_us_frequency_item_type_validator(self, value):
        """
            A validator for NUM US Frequency concept.

            Args:
                value (decimal or int or str): value to be validated and converted if needed

            Returns:
                A Tuple (decimal or int or str, list of str) containing original or converted value
                and list of errors (if any)
        """
        return self._xbrli_decimal_item_type_validator(value)

    def _num_us_insolation_item_type_validator(self, value):
        """
            A validator for NUM US Insolation concept.

            Args:
                value (decimal or int or str): value to be validated and converted if needed

            Returns:
                A Tuple (decimal or int or str, list of str) containing original or converted value
                and list of errors (if any)
        """
        return self._xbrli_decimal_item_type_validator(value)

    def _num_us_irradiance_item_type_validator(self, value):
        """
            A validator for NUM US Irradience concept.

            Args:
                value (decimal or int or str): value to be validated and converted if needed

            Returns:
                A Tuple (decimal or int or str, list of str) containing original or converted value
                and list of errors (if any)
        """
        return self._xbrli_decimal_item_type_validator(value)

    def _num_us_plane_angle_item_type_validator(self, value):
        """
            A validator for NUM US Plane Angle concept.

            Args:
                value (decimal or int or str): value to be validated and converted if needed

            Returns:
                A Tuple (decimal or int or str, list of str) containing original or converted value
                and list of errors (if any)
        """
        return self._xbrli_decimal_item_type_validator(value)

    def _num_us_pressure_item_type_validator(self, value):
        """
            A validator for NUM US Pressure concept.

            Args:
                value (decimal or int or str): value to be validated and converted if needed

            Returns:
                A Tuple (decimal or int or str, list of str) containing original or converted value
                and list of errors (if any)
        """
        return self._xbrli_decimal_item_type_validator(value)

    def _num_us_speed_item_type_validator(self, value):
        """
            A validator for NUM US Speed concept.

            Args:
                value (decimal or int or str): value to be validated and converted if needed

            Returns:
                A Tuple (decimal or int or str, list of str) containing original or converted value
                and list of errors (if any)
        """
        return self._xbrli_decimal_item_type_validator(value)

    def _num_us_temperature_item_type_validator(self, value):
        """
            A validator for NUM US Temperature concept.

            Args:
                value (decimal or int or str): value to be validated and converted if needed

            Returns:
                A Tuple (decimal or int or str, list of str) containing original or converted value
                and list of errors (if any)
        """
        return self._xbrli_decimal_item_type_validator(value)

    def _num_us_voltage_item_type_validator(self, value):
        """
            A validator for NUM US Plane Angle concept.

            Args:
                value (decimal or int or str): value to be validated and converted if needed

            Returns:
                A Tuple (decimal or int or str, list of str) containing original or converted value
                and list of errors (if any)
        """
        return self._xbrli_decimal_item_type_validator(value)

    def _num_area_item_type_validator(self, value):
        """
            A validator for NUM Area concept.

            Args:
                value (decimal or int or str): value to be validated and converted if needed

            Returns:
                A Tuple (decimal or int or str, list of str) containing original or converted value
                and list of errors (if any)
        """
        return self._xbrli_decimal_item_type_validator(value)

    def _num_energy_item_type_validator(self, value):
        """
            A validator for NUM Energy concept.

            Args:
                value (decimal or int or str): value to be validated and converted if needed

            Returns:
                A Tuple (decimal or int or str, list of str) containing original or converted value
                and list of errors (if any)
        """
        return self._xbrli_decimal_item_type_validator(value)

    def _num_length_item_type_validator(self, value):
        """
            A validator for NUM Length concept.

            Args:
                value (decimal or int or str): value to be validated and converted if needed

            Returns:
                A Tuple (decimal or int or str, list of str) containing original or converted value
                and list of errors (if any)
        """
        return self._xbrli_decimal_item_type_validator(value)

    def _num_mass_item_type_validator(self, value):
        """
            A validator for NUM Mass concept.

            Args:
                value (decimal or int or str): value to be validated and converted if needed

            Returns:
                A Tuple (decimal or int or str, list of str) containing original or converted value
                and list of errors (if any)
        """
        return self._xbrli_decimal_item_type_validator(value)

    def _num_volume_item_type_validator(self, value):
        """
            A validator for NUM Volume concept.

            Args:
                value (decimal or int or str): value to be validated and converted if needed

            Returns:
                A Tuple (decimal or int or str, list of str) containing original or converted value
                and list of errors (if any)
        """
        return self._xbrli_decimal_item_type_validator(value)
