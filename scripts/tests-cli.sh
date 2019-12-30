#!/bin/bash

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

EXITVAL=0

# Basic tests
python scripts/cli/cli.py -h || {
    EXITVAL=1
}
python scripts/cli/cli.py --help || {
    EXITVAL=1
}
python scripts/cli/cli.py info || {
    EXITVAL=1
}
python scripts/cli/cli.py version || {
    EXITVAL=1
}

# Identifier tests
python scripts/cli/cli.py generate-identifier || {
    EXITVAL=1
}
python scripts/cli/cli.py validate-identifier 55db4ff3-5136-4be5-846b-4a93eb4c576d || {
    EXITVAL=1
}
python scripts/cli/cli.py validate-identifier 55db4ff3-5136-4be5-846b-4a93eb4c576 || {
    EXITVAL=1
}
  
# Units tests
python scripts/cli/cli.py taxonomy list-units || {
    EXITVAL=1
}
python scripts/cli/cli.py taxonomy list-units-details || {
    EXITVAL=1
}
python scripts/cli/cli.py --csv taxonomy list-units-details || {
    EXITVAL=1
}
python scripts/cli/cli.py taxonomy list-unit-details rad || {
    EXITVAL=1
}
python scripts/cli/cli.py taxonomy validate-unit rad || {
    EXITVAL=1
}

# Numeric type tests
python scripts/cli/cli.py taxonomy list-numeric-types || {
    EXITVAL=1
}
python scripts/cli/cli.py taxonomy validate-numeric-type electricCurrentItemType || {
    EXITVAL=1
}
python scripts/cli/cli.py taxonomy validate-numeric-type electricCurrentIteType || {
    EXITVAL=1
}

# Types test
python scripts/cli/cli.py taxonomy list-type-enums climateZoneANSIItemType || {
    EXITVAL=1
}
python scripts/cli/cli.py taxonomy validate-type climateZoneANSIItemType || {
    EXITVAL=1
}
python scripts/cli/cli.py taxonomy validate-type climateZoneANSIItemype || {
    EXITVAL=1
}
python scripts/cli/cli.py taxonomy list-types || {
    EXITVAL=1
}

# Semantic tests
python scripts/cli/cli.py taxonomy validate-entrypoint MonthlyOperatingReport || {
    EXITVAL=1
}
python scripts/cli/cli.py taxonomy validate-entrypoint MonthlyOperatngReport || {
    EXITVAL=1
}
python scripts/cli/cli.py taxonomy list-concepts MonthlyOperatingReport || {
    EXITVAL=1
}
python scripts/cli/cli.py taxonomy list-concepts-details MonthlyOperatingReport || {
    EXITVAL=1
}
python scripts/cli/cli.py taxonomy list-concept-details solar:AccountsReceivableCustomerName || {
    EXITVAL=1
}
python scripts/cli/cli.py --csv taxonomy list-concepts-details MonthlyOperatingReport || {
    EXITVAL=1
}
python scripts/cli/cli.py taxonomy list-entrypoints || {
    EXITVAL=1
}
python scripts/cli/cli.py taxonomy list-entrypoints-details || {
    EXITVAL=1
}
python scripts/cli/cli.py --csv taxonomy list-entrypoints || {
    EXITVAL=1
}
python scripts/cli/cli.py --csv taxonomy list-entrypoints-details || {
    EXITVAL=1
}
python scripts/cli/cli.py taxonomy list-entrypoint-details Site || {
    EXITVAL=1
}
python scripts/cli/cli.py taxonomy validate-concept solar:AccountsReceivableCustomerName || {
    EXITVAL=1
}
python scripts/cli/cli.py taxonomy validate-value solar:AccountsReceivableCustomerName George || {
    EXITVAL=1
}
python scripts/cli/cli.py taxonomy validate-value solar:AccountsReceivableCustomerName George || {
    EXITVAL=1
}
python scripts/cli/cli.py taxonomy list-concepts-details MonthlyOperatingReport || {
    EXITVAL=1
}
python scripts/cli/cli.py taxonomy list-relationships MonthlyOperatingReport || {
    EXITVAL=1
}
python scripts/cli/cli.py --csv taxonomy list-relationships MonthlyOperatingReport || {
    EXITVAL=1
}

# Ref parts tests
python scripts/cli/cli.py taxonomy list-ref-parts || {
    EXITVAL=1
}
python scripts/cli/cli.py taxonomy validate-ref-part Dimension || {
    EXITVAL=1
}
python scripts/cli/cli.py taxonomy validate-ref-part Dimnsion || {
    EXITVAL=1
}

# Generic roles tests
python scripts/cli/cli.py taxonomy list-generic-roles || {
    EXITVAL=1
}
python scripts/cli/cli.py taxonomy validate-generic-role "Generic UML composition arc" || {
    EXITVAL=1
}
python scripts/cli/cli.py taxonomy validate-generic-role "Generic UML compositin arc" || {
    EXITVAL=1
}

# Documentation test
python scripts/cli/cli.py taxonomy list-concept-documentation solar:Curtailment || {
    EXITVAL=1
}

# Validation and conversion tests
mkdir temp
cat > temp/in.json <<- EOM
{
  "documentType": "http://www.xbrl.org/WGWD/YYYY-MM-DD/xbrl-json",
  "prefixes": {
    "xmlns": "http://www.xbrl.org/2003/instance",
    "xmlns:link": "http://www.xbrl.org/2003/linkbase",
    "xmlns:xlink": "http://www.w3.org/1999/xlink",
    "xmlns:xsi": "http://www.w3.org/2001/XMRLSchema-instance",
    "xmlns:units": "http://www.xbrl.org/2009/utr",
    "xmlns:xbrldi": "http://xbrl.org/2006/xbrldi",
    "xmlns:solar": "http://xbrl.us/Solar/2019-09-20/solar"
  },
  "dtsReferences": [
    {
      "type": "schema",
      "href": "https://raw.githubusercontent.com/xbrlus/solar/core/solar_2019-09-20.xsd"
    }
  ],
  "facts": {
    "98d526c7-0922-4b7c-9db6-fe81905277f6": {
      "aspects": {
        "entity": "JUPITER",
        "period": "2017-11-01T00:00:00/2017-11-30T00:00:00",
        "concept": "solar:MonthlyOperatingReportAvailabilityOfDocument"
      },
      "value": "True"
    },
    "043801d0-7552-4dbd-b346-d6ce2b69a916": {
      "aspects": {
        "entity": "JUPITER",
        "period": "2017-11-01T00:00:00/2017-11-30T00:00:00",
        "concept": "solar:MonthlyOperatingReportAvailabilityOfFinalDocument"
      },
      "value": "True"
    },
    "4f4dd3cc-88b6-4912-b905-c1b9659414bd": {
      "aspects": {
        "entity": "JUPITER",
        "period": "2017-11-01T00:00:00/2017-11-30T00:00:00",
        "concept": "solar:MonthlyOperatingReportAvailabilityOfDocumentExceptions"
      },
      "value": "False"
    },
    "bac24db9-82ac-4e1e-b3a7-e4f89eeb1f82": {
      "aspects": {
        "entity": "JUPITER",
        "period": "2017-11-01T00:00:00/2017-11-30T00:00:00",
        "concept": "solar:MonthlyOperatingReportExceptionDescription"
      },
      "value": "None"
    },
    "e1de6f73-1f87-4f9d-bc7c-f2c316b80444": {
      "aspects": {
        "entity": "JUPITER",
        "period": "2017-11-01T00:00:00/2017-11-30T00:00:00",
        "concept": "solar:MonthlyOperatingReportCounterparties"
      },
      "value": "None"
    },
    "ac5cb77b-31f0-487b-bb3a-4c26774379b7": {
      "aspects": {
        "entity": "JUPITER",
        "period": "2017-11-01T00:00:00/2017-11-30T00:00:00",
        "concept": "solar:MonthlyOperatingReportEffectiveDate"
      },
      "value": "2017-11-01"
    },
    "6c5c2192-3805-4570-af5b-41efd74dd485": {
      "aspects": {
        "entity": "JUPITER",
        "period": "2017-11-01T00:00:00/2017-11-30T00:00:00",
        "concept": "solar:MonthlyOperatingReportEndDate"
      },
      "value": "2017-11-30"
    },
    "16e8f8c0-db6d-46ce-a838-b6f3ed2a9f50": {
      "aspects": {
        "entity": "JUPITER",
        "period": "2017-11-01T00:00:00/2017-11-30T00:00:00",
        "concept": "solar:MonthlyOperatingReportDocumentLink"
      },
      "value": "None"
    },
    "4b27ce28-bb51-4418-a9d3-e240fd743d8b": {
      "aspects": {
        "entity": "JUPITER",
        "period": "2017-11-01T00:00:00/2017-11-30T00:00:00",
        "concept": "solar:MonthlyOperatingReportPreparerName"
      },
      "value": "JUPITER"
    }
  }
}
EOM

cat > temp/in.xml <<- EOM
<xbrl
    xmlns="http://www.xbrl.org/2003/instance"
    xmlns:link="http://www.xbrl.org/2003/linkbase"
    xmlns:solar="http://xbrl.us/Solar/2019-09-20/solar"
    xmlns:units="http://www.xbrl.org/2009/utr"
    xmlns:xbrldi="http://xbrl.org/2006/xbrldi"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:xsi="http://www.w3.org/2001/XMRLSchema-instance">
    <link:schemaRef xlink:href="https://raw.githubusercontent.com/xbrlus/solar/v1.2/core/solar_2018-03-31_r01.xsd" xlink:type="simple" />
    <unit id="kW">
        <measure>units:kW</measure>
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
</xbrl>
EOM

# Test with default name recognition
python scripts/cli/cli.py validate temp/in.json || {
    EXITVAL=1
}
python scripts/cli/cli.py validate --entrypoint=System temp/in.xml || {
    EXITVAL=1
}
python scripts/cli/cli.py convert temp/in.json temp/out.xml || {
    EXITVAL=1
}
python scripts/cli/cli.py convert --entrypoint=System temp/in.xml temp/out.json || {
    EXITVAL=1
}

# Test with names that cannot be automatically recognized
cp temp/in.json temp/in.jsoon
cp temp/in.xml temp/in.xmml
python scripts/cli/cli.py --json validate temp/in.jsoon || {
    EXITVAL=1
}
python scripts/cli/cli.py --xml validate --entrypoint=System temp/in.xmml || {
    EXITVAL=1
}
python scripts/cli/cli.py --json convert temp/in.jsoon temp/out2.xml || {
    EXITVAL=1
}
python scripts/cli/cli.py --xml convert --entrypoint=System temp/in.xml temp/out.json || {
    EXITVAL=1
}

# Clean up
rm -rf temp

# Print results and exit
echo ""
if [[ $EXITVAL -eq 0 ]]
then
    echo "Tests completed successfully"
else
    echo "Some tests were unsuccesful"
fi

exit $EXITVAL
