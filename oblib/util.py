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
Contains basic utility methods used throughout the library.  Please note that this file is not
exported as part of the module so if a method has an external signature place it somewhere else.
"""

import datetime


def convert_taxonomy_xsd_bool(inp):
    """ 
    Returns true/false given a string loaded from the Taxonomy.  Values to check are based on
    observed values from within the Taxonomy.  If the input is not valid this will always return
    false.

    Args:
        inp (string): String containing booleans in Taxonomy XSD format.

    Returns:
        True or False
    """

    if inp is None:
        return False
    elif inp.strip().lower() in ["true", "1"]:
        return True
    else:
        return False


def convert_taxonomy_xsd_date(inp):
    """
    Returns a datetime representation of a date (in string format) loaded from the taxonomy.  It
    is assumed that the input format will be YYYY-MM-DD based upon observed values from within 
    the taxonomy.  
    
    If the input is not valid this will return none.  At this point in time this function does
    not require MM and DD to be two digits since there does not appear to be any reason to reject
    data with these two validation errors.

    Args:
        inp (string): String containning dates in Taxonomy XSD format.

    Returns:
        True or False
    """

    try:
        return datetime.datetime.strptime(inp, "%Y-%m-%d").date()
    except ValueError:
        return None


def convert_json_datetime(inp):
    """
    Converts a JSON data time value based upon the XBRL JSON specification format.

    Args:
        inp (string): String containning dates in Taxonomy XSD format.

    Returns:
        datetime
    """

    try:
        return datetime.datetime.strptime(inp, "%Y-%m-%dT%H:%M:%S").date()
    except ValueError:
        return None
