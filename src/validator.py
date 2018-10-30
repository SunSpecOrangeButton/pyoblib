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


def validate_concept_value(concept, value):

    # If null check if nillable is ok and return
    if value is None and concept.nillable:
        return True
    elif value is None and not concept.nillable:
        return False

    # Check data type
    #
    # TODO: This is neither a complete list nor does it take into consideration string values that
    # contain legal representations.  Its very basic at this point of time and needs to be hashed
    # out.
    #
    if concept.type_name == "xbrli:booleanItemType":
        if type(value) is not bool:
            return False
    elif concept.type_name == "xbrli:stringItemType":
        if type(value) is not str:
            return False
    elif concept.type_name == "xbrli:integerItemType":
        if type(value) is not int:
            return False

    # Check identifiers.  This is based upon the name of the field containing the word Identifier
    # in it.
    if concept.id.find("Identifier") != -1:
        return identifier.validate(value)

    # If all conditions clear then the value passes.
    return True
