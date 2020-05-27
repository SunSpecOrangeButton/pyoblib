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


# The following constants are based on hard-coded dates found in other modules.  Moving all of them into constants
# is a first step towards standardization.  The second step will be analysis to see if some of them can be combined
# and a potential third step will be to move away from hardcoding altogether.

XML_NS = {"xbrldi:": "{http://xbrl.org/2006/xbrldi}",
      "link:": "{http://www.xbrl.org/2003/linkbase}",
      "solar:": "{http://xbrl.us/Solar/2020-04-01/solar}",
      "dei:": "{http://xbrl.sec.gov/dei/2014-01-31}",
      "us-gaap:": "{http://fasb.org/us-gaap/2017-01-31}"}

XBRL_ORG_INSTANCE = "{http://www.xbrl.org/2003/instance}"

DEI_NS = "{http://xbrl.sec.gov/dei/2014-01-31}"

GAAP_NS = "{http://fasb.org/us-gaap/2017-01-31}"

SOLAR_NS = "{http://xbrl.us/Solar/2020-04-01/solar}"

TAXONOMY_ALL_FILENAME = "solar_all_2020-04-01_def.xml"

ROLE_DOCUMENTATION = "http://www.xbrl.org/2003/role/documentation"

OPTIONAL_NAMESPACES = {
    "us-gaap": "http://xbrl.fasb.org/us-gaap/2017/elts/us-gaap-2017-01-31.xsd"
}

NAMESPACES = {
    "xmlns": "http://www.xbrl.org/2003/instance",
    "xmlns:link": "http://www.xbrl.org/2003/linkbase",
    "xmlns:xlink": "http://www.w3.org/1999/xlink",
    "xmlns:xsi": "http://www.w3.org/2001/XMRLSchema-instance",
    "xmlns:units": "http://www.xbrl.org/2009/utr",
    "xmlns:xbrldi": "http://xbrl.org/2006/xbrldi",
    "xmlns:solar": "http://xbrl.us/Solar/2020-04-01/solar"
}

TAXONOMY_NAME = "https://raw.githubusercontent.com/SunSpecOrangeButton/solar-taxonomy/master/core/solar_all_2020-04-01.xsd"

DEI_XSD = "dei-2018-01-31.xsd"

US_GAAP_XSD = "us-gaap-2017-01-31.xsd"

SOLAR_XSD = "solar_2020-04-01.xsd"

SOLAR_ALL_PRE_XML = "solar_all_2020-04-01_pre.xml"

SOLAR_LAB_XML = "solar_2020-04-01_lab.xml"

SOLAR_CALCULATION_XML = "solar_all_2020-04-01_cal.xml"
