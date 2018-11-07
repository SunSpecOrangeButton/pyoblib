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

import re
import uuid

REG_EX = "^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"

def identifier():
    """
    Returns valid UUID for Orange Button identifiers
    """
    return  str(uuid.uuid4())

def validate(inp):
    """
    Validates that a particular string is either a valid UUID or not a valid UUID.
    """
    return re.search(REG_EX, inp, re.IGNORECASE) is not None
