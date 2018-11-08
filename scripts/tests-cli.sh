#!/bin/bash

# Copyright 2018 Wells Fargo

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

export PYTHONPATH=`pwd`/src/obcore
EXITVAL=0

# Basic tests
python src/obcli/cli.py -h || {
    EXITVAL=1
}
python src/obcli/cli.py --help || {
    EXITVAL=1
}
python src/obcli/cli.py info || {
    EXITVAL=1
}
python src/obcli/cli.py version || {
    EXITVAL=1
}

# Identifier tests
python src/obcli/cli.py generate-identifier || {
    EXITVAL=1
}
python src/obcli/cli.py validate-identifier 55db4ff3-5136-4be5-846b-4a93eb4c576d || {
    EXITVAL=1
}
python src/obcli/cli.py validate-identifier 55db4ff3-5136-4be5-846b-4a93eb4c576 || {
    EXITVAL=1
}
  
# Units tests
python src/obcli/cli.py taxonomy list-units || {
    EXITVAL=1
}
python src/obcli/cli.py taxonomy list-units-details || {
    EXITVAL=1
}
python src/obcli/cli.py taxonomy list-unit-info rad || {
    EXITVAL=1
}
python src/obcli/cli.py taxonomy validate-unit rad || {
    EXITVAL=1
}

# Numeric type tests
python src/obcli/cli.py taxonomy list-numeric-types || {
    EXITVAL=1
}
python src/obcli/cli.py taxonomy validate-numeric-type electricCurrentItemType || {
    EXITVAL=1
}
python src/obcli/cli.py taxonomy validate-numeric-type electricCurrentIteType || {
    EXITVAL=1
}

# Types test
python src/obcli/cli.py taxonomy list-type-enums climateZoneANSIItemType || {
    EXITVAL=1
}
python src/obcli/cli.py taxonomy validate-type climateZoneANSIItemType || {
    EXITVAL=1
}
python src/obcli/cli.py taxonomy validate-type climateZoneANSIItemype || {
    EXITVAL=1
}

# Semantic tests
python src/obcli/cli.py taxonomy validate-ep MonthlyOperatingReport || {
    EXITVAL=1
}
python src/obcli/cli.py taxonomy validate-ep MonthlyOperatngReport || {
    EXITVAL=1
}
python src/obcli/cli.py taxonomy list-concepts MonthlyOperatingReport || {
    EXITVAL=1
}
python src/obcli/cli.py taxonomy list-concepts-info MonthlyOperatingReport || {
    EXITVAL=1
}
python src/obcli/cli.py taxonomy list-concept-info solar:AccountsReceivableCustomerName || {
    EXITVAL=1
}
python src/obcli/cli.py taxonomy validate-concept solar:AccountsReceivableCustomerName || {
    EXITVAL=1
}
python src/obcli/cli.py taxonomy validate-value solar:AccountsReceivableCustomerName George || {
    EXITVAL=1
}

# Ref parts tests
python src/obcli/cli.py taxonomy list-ref-parts || {
    EXITVAL=1
}
python src/obcli/cli.py taxonomy validate-ref-part Dimension || {
    EXITVAL=1
}
python src/obcli/cli.py taxonomy validate-ref-part Dimnsion || {
    EXITVAL=1
}

# Generic roles tests
python src/obcli/cli.py taxonomy list-generic-roles || {
    EXITVAL=1
}
python src/obcli/cli.py taxonomy validate-generic-role "Generic UML composition arc" || {
    EXITVAL=1
}
python src/obcli/cli.py taxonomy validate-generic-role "Generic UML compositin arc" || {
    EXITVAL=1
}

exit $EXITVAL
