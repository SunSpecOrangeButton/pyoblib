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

"""
Contains generic classes and methods used throughout oblib including but not limited
to Error classes.
"""

import datetime


class OBError(Exception):
    """
    Base class for Orange Button data validity exceptions.
    """
    def __init__(self, message):
        super(OBError, self).__init__(message)


class OBTypeError(OBError):
    """
    Raised if we try to set a concept to a value with an invalid data type
    """
    def __init__(self, message):
        super(OBTypeError, self).__init__(message)


class OBContextError(OBError):
    """
    Raised if we try to set a concept without sufficient Context fields
    """
    def __init__(self, message):
        super(OBContextError, self).__init__(message)


class OBConceptError(OBError):
    """
    Raised if we try to set a concept that can't be set in the current
    Entrypoint
    """
    def __init__(self, message):
        super(OBConceptError, self).__init__(message)


class OBNotFoundError(OBError):
    """
    Raised if we refer to a name that's not found in the taxonomy
    """
    def __init__(self, message):
        super(OBNotFoundError, self).__init__(message)


class OBUnitError(OBError):
    """
    Raised if we try to set a concept to a value with incorrect units
    """
    def __init__(self, message):
        super(OBUnitError, self).__init__(message)


class OBValidationError(OBError):
    """
    Raised during validation of input data if any portion of code raises an error
    """
    def __init__(self, message):
        super(OBValidationError, self).__init__(message)


class OBMultipleErrors(OBError):
    """
    Raised in sections of code which must group errors together and raise them
    as a set of functions.
    """

    def __init__(self, message, validation_errors=None):
        super(OBMultipleErrors, self).__init__(message)
        if validation_errors is not None:
            self._errors = validation_errors
        else:
            self._errors = []

    def append(self, error):
        """
        Appends an exception to the list internally held list of errors.

        Args:
            error (any type): If this is a type inherited from OBError it will be
            added to the end of the list.  If it is type inherited from OBMultipleErrors
            the lists will be concatenated.  If it is a string it will be converted to
            a OBError.  If it is any other type it will be converted to a string and
            then an OBError will be created using the string as a message.
        """

        if isinstance(error, OBMultipleErrors):
            self._errors = self._errors + error.get_errors()
        elif isinstance(error, OBError):
            self._errors.append(error)
        elif isinstance(error, str):
            self._errors.append(OBError(error))
        else:
            self._errors.append(OBError(str(error)))

    def get_errors(self):
        """
        Used to access the list of errors.

        Returns:
             List of OBErrors.
        """
        return self._errors


class OBValidationErrors(OBMultipleErrors):
    """
    Raised in sections of code that must return lists of validaition errors.
    """
    def __init__(self, message):
        super(OBValidationErrors, self).__init__(message)