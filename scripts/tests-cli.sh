#!/bin/bash

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

export PYTHONPATH=`pwd`/src
EXITVAL=0

# Basic tests
python src-cli/cli.py -h || {
    EXITVAL=1
}
python src-cli/cli.py --help || {
    EXITVAL=1
}
python src-cli/cli.py info || {
    EXITVAL=1
}
python src-cli/cli.py version || {
    EXITVAL=1
}

# Identifier tests
python src-cli/cli.py generate-identifier || {
    EXITVAL=1
}
python src-cli/cli.py validate-identifier 55db4ff3-5136-4be5-846b-4a93eb4c576d || {
    EXITVAL=1
}
python src-cli/cli.py validate-identifier 55db4ff3-5136-4be5-846b-4a93eb4c576 || {
    EXITVAL=1
}
  
# Units tests
python src-cli/cli.py list-units || {
    EXITVAL=1
}
python src-cli/cli.py list-units-details || {
    EXITVAL=1
}
python src-cli/cli.py list-unit-info rad || {
    EXITVAL=1
}
python src-cli/cli.py validate-unit rad || {
    EXITVAL=1
}

# Numeric type tests
python src-cli/cli.py list-numeric-types || {
    EXITVAL=1
}
python src-cli/cli.py validate-numeric-type electricCurrentItemType || {
    EXITVAL=1
}
python src-cli/cli.py validate-numeric-type electricCurrentIteType || {
    EXITVAL=1
}

# Types test
python src-cli/cli.py list-type-enums climateZoneANSIItemType || {
    EXITVAL=1
}
python src-cli/cli.py validate-type climateZoneANSIItemType || {
    EXITVAL=1
}
python src-cli/cli.py validate-type climateZoneANSIItemype || {
    EXITVAL=1
}

# Semantic tests
python src-cli/cli.py validate-ep MonthlyOperatingReport || {
    EXITVAL=1
}
python src-cli/cli.py validate-ep MonthlyOperatngReport || {
    EXITVAL=1
}
python src-cli/cli.py list-concepts MonthlyOperatingReport || {
    EXITVAL=1
}
python src-cli/cli.py list-concepts-info MonthlyOperatingReport || {
    EXITVAL=1
}
python src-cli/cli.py list-concept-info solar:AccountsReceivableCustomerName || {
    EXITVAL=1
}
python src-cli/cli.py validate-concept solar:AccountsReceivableCustomerName || {
    EXITVAL=1
}
python src-cli/cli.py validate-value solar:AccountsReceivableCustomerName George || {
    EXITVAL=1
}

# Ref parts tests
python src-cli/cli.py list-ref-parts || {
    EXITVAL=1
}
python src-cli/cli.py validate-ref-part Dimension || {
    EXITVAL=1
}
python src-cli/cli.py validate-ref-part Dimnsion || {
    EXITVAL=1
}

# Generic roles tests
python src-cli/cli.py list-generic-roles || {
    EXITVAL=1
}
python src-cli/cli.py validate-generic-role "Generic UML composition arc" || {
    EXITVAL=1
}
python src-cli/cli.py validate-generic-role "Generic UML compositin arc" || {
    EXITVAL=1
}

exit $EXITVAL
