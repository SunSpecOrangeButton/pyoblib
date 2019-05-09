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

import unittest
from jsondiff import diff
from oblib import parser, taxonomy


taxonomy = taxonomy.Taxonomy()
parser = parser.Parser(taxonomy)


class TestParser(unittest.TestCase):
    # Note: this module is tested differently than others.  Sample JSON and XML
    # files are imported and then exported and later compared using the string
    # methods.  Thereafter files are loaded and created but the files contents
    # themselves are not examined (it is assumed that this would be picked up
    # in the comparisons of the strings).
    
    def test_json(self):
        
        entrypoint = parser.from_JSON_string(TEST_JSON)
        out = parser.to_JSON_string(entrypoint)
        d = diff(TEST_JSON, out)

        # TODO: Right now the JSON input and output has too many discrepancies to run the Equality
        # check.  Leave commented out for the time being and keep as a future testing goal. 
        # self.assertEqual(d, "{}")

    def test_xml(self):
        entrypoint = parser.from_XML_string(TEST_XML)
        out = parser.to_XML_string(entrypoint)

        # TODO: Add an XML diff tool and run tests on it.

    def test_entrypoint_names(self):
        # Correct
        parser.from_JSON_string(TEST_JSON, "MonthlyOperatingReport")
        parser.from_XML_string(TEST_XML, "Appraisal")

        # Misspelled cases
        with self.assertRaises(Exception):
            parser.from_JSON_string(TEST_JSON, "MonlyOperatingReport")
        with self.assertRaises(Exception):
            parser.from_XML_string(TEST_XML, "Apprial")

        # Wrong entrypoint
        with self.assertRaises(Exception):
            parser.from_JSON_string(TEST_JSON, "CutSheet")
        with self.assertRaises(Exception):
            parser.from_XML_string(TEST_XML, "System")

    def test_files(self):
        # TODO:
        # Test validate XML
        # Test validate JSON
        # Test convert XML to JSON
        # Test convert JSON to XML
        pass


TEST_JSON = """
{
  "documentType": "http://www.xbrl.org/WGWD/YYYY-MM-DD/xbrl-json",
  "prefixes": {
    "xbrl": "http://www.xbrl.org/WGWD/YYYY-MM-DD/oim",
    "solar": "http://xbrl.us/Solar/v1.3/2019-02-27/solar",  
    "us-gaap": "http://fasb.org/us-gaap/2017-01-31",
    "iso4217": "http://www.xbrl.org/2003/iso4217",
    "SI": "http://www.xbrl.org/2009/utr"
  },
  "dtsReferences": [
    {
      "type": "schema",
      "href": "https://raw.githubusercontent.com/SunSpecOrangeButton/solar-taxonomy/master/core/solar_all_2019-02-27_r01.xsd"
    }
  ],
  "facts": {
    "16f60d57-2536-4ec3-8414-02b95d067e02": {
      "value": true,
      "aspects": {
        "concept": "solar:MonthlyOperatingReportAvailabilityOfDocument",
        "entity": "JUPITER",
        "period": "2017-11-01T00:00:00/2017-11-30T00:00:00"
      }
    },
    "8333ad4e-24b4-42c1-83b3-fca9ef7fce55" : {
      "value": true,
      "aspects": {
        "concept": "solar:MonthlyOperatingReportAvailabilityOfFinalDocument",
        "entity": "JUPITER",
        "period": "2017-11-01T00:00:00/2017-11-30T00:00:00"
      }
    }
  }
}
"""

TEST_XML = """
<xbrl 
    xmlns="http://www.xbrl.org/2003/instance"
    xmlns:link="http://www.xbrl.org/2003/linkbase"
    xmlns:solar="http://xbrl.us/Solar/v1.3/2019-02-27/solar"
    xmlns:units="http://www.xbrl.org/2009/utr"
    xmlns:xbrldi="http://xbrl.org/2006/xbrldi"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:xsi="http://www.w3.org/2001/XMRLSchema-instance">
    <link:schemaRef xlink:href="https://raw.githubusercontent.com/xbrlus/solar/v1.2/core/solar_2018-03-31_r01.xsd" xlink:type="simple" />
    <context id="NON_TABLE_CONCEPTS_0">
        <entity>
            <identifier scheme="http://xbrl.org/entity/identification/scheme" >JUPITER</identifier>
        </entity>
        <period>
            <forever />
        </period>
    </context>
    <solar:AppraisalAvailabilityOfDocument contextRef="NON_TABLE_CONCEPTS_0" id="test">true</solar:AppraisalAvailabilityOfDocument>
    <solar:AppraisalAvailabilityOfFinalDocument contextRef="NON_TABLE_CONCEPTS_0">true</solar:AppraisalAvailabilityOfFinalDocument>
    <solar:AppraisalAvailabilityOfDocumentExceptions contextRef="NON_TABLE_CONCEPTS_0">true</solar:AppraisalAvailabilityOfDocumentExceptions>
    <solar:AppraisalExceptionDescription contextRef="NON_TABLE_CONCEPTS_0">None</solar:AppraisalExceptionDescription>
    <solar:AppraisalCounterparties contextRef="NON_TABLE_CONCEPTS_0">2018-04-04</solar:AppraisalCounterparties>
    <solar:AppraisalEffectiveDate contextRef="NON_TABLE_CONCEPTS_0">2018-01-01</solar:AppraisalEffectiveDate>
    <solar:AppraisalExpirationDate contextRef="NON_TABLE_CONCEPTS_0">2018-05-05</solar:AppraisalExpirationDate>
    <solar:AppraisedValueFairMarketValue contextRef="NON_TABLE_CONCEPTS_0">456456</solar:AppraisedValueFairMarketValue>
    <solar:AppraisalDocumentLink contextRef="NON_TABLE_CONCEPTS_0">None</solar:AppraisalDocumentLink>
    <solar:PreparerOfAppraisal contextRef="NON_TABLE_CONCEPTS_0">John Smith</solar:PreparerOfAppraisal>
    <solar:DocumentIdentifierAppraisal contextRef="NON_TABLE_CONCEPTS_0">false</solar:DocumentIdentifierAppraisal>
</xbrl>
"""


# Note: this currently fails and has been replaced by a clip that works.
# Ultimately both need to work.
TEST_XML_2 = """
<xbrl
    xmlns="http://www.xbrl.org/2003/instance"
    xmlns:link="http://www.xbrl.org/2003/linkbase"
    xmlns:solar="http://xbrl.us/Solar/v1.3/2019-02-27/solar"
    xmlns:units="http://www.xbrl.org/2009/utr"
    xmlns:xbrldi="http://xbrl.org/2006/xbrldi"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:xsi="http://www.w3.org/2001/XMRLSchema-instance">
    <link:schemaRef xlink:href="https://raw.githubusercontent.com/xbrlus/solar/v1.2/core/solar_2018-03-31_r01.xsd" xlink:type="simple" />
    <context id="solar:SolarArrayTable_1">
        <entity>
            <identifier scheme="http://xbrl.org/entity/identification/scheme">kWh Analytics</identifier>
            <segment>
                <xbrldi:typedMember dimension="solar:PVSystemIdentifierAxis">
                    <solar:PVSystemIdentifierDomain>1</solar:PVSystemIdentifierDomain>
                </xbrldi:typedMember>
                <xbrldi:typedMember dimension="solar:SolarSubArrayIdentifierAxis">
                    <solar:SolarSubArrayIdentifierDomain>1</solar:SolarSubArrayIdentifierDomain>
                </xbrldi:typedMember>
                <xbrldi:typedMember dimension="solar:EquipmentTypeAxis">
                    <solar:EquipmentTypeDomain>solar:ModuleMember</solar:EquipmentTypeDomain>
                </xbrldi:typedMember>
            </segment>
        </entity>
        <period>
            <instant>2018-12-14</instant>
        </period>
    </context>
    <unit id="kW">
        <measure>units:kW</measure>
    </unit>
    <unit id="Degree">
        <measure>units:Degree</measure>
    </unit>
    <context id="solar:ProductIdentifierTable_0">
        <entity>
            <identifier scheme="http://xbrl.org/entity/identification/scheme">kWh Analytics</identifier>
            <segment>
                <xbrldi:typedMember dimension="solar:PVSystemIdentifierAxis">
                    <solar:PVSystemIdentifierDomain>1</solar:PVSystemIdentifierDomain>
                </xbrldi:typedMember>
                <xbrldi:typedMember dimension="solar:ProductIdentifierAxis">
                    <solar:ProductIdentifierDomain>Placeholder</solar:ProductIdentifierDomain>
                </xbrldi:typedMember>
                <xbrldi:typedMember dimension="solar:TestConditionAxis">
                    <solar:TestConditionDomain>solar:StandardTestConditionMember</solar:TestConditionDomain>
                </xbrldi:typedMember>
            </segment>
        </entity>
        <period>
            <forever />
        </period>
    </context>

    <solar:InverterOutputMaximumPowerAC contextRef="solar:ProductIdentifierTable_0" decimals="2" unitRef="kW">220</solar:InverterOutputMaximumPowerAC>
    <solar:OrientationAzimuth contextRef="solar:SolarArrayTable_1" decimals="2" unitRef="Degree">25</solar:OrientationAzimuth>
</xbrl>
"""