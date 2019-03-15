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
Sets pyoblib constants.
    SOLAR_TAXONOMY_DIR : path to solar taxonomy.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

if getattr( sys, 'frozen', False ) :
    # Running in a bundle (pyinstaller)
    SOLAR_TAXONOMY_DIR = os.path.join(sys._MEIPASS, "solar-taxonomy")
else:
    # Running from source
    SOLAR_TAXONOMY_DIR = os.path.join(BASE_DIR, "data", "solar-taxonomy")
