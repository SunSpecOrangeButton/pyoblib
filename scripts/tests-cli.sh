#!/bin/bash

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
    echo Failed
    EXITVAL=1
}
python src-cli/cli.py --help || {
    echo Failed
    EXITVAL=1
}
python src-cli/cli.py info || {
    echo Failed
    EXITVAL=1
}
python src-cli/cli.py version || {
    echo Failed
    EXITVAL=1
}

# Identifier tests
python src-cli/cli.py generate-identifier || {
    echo Failed
    EXITVAL=1
}
python src-cli/cli.py validate-identifier 55db4ff3-5136-4be5-846b-4a93eb4c576d || {
    echo Failed
    EXITVAL=1
}
python src-cli/cli.py validate-identifier 55db4ff3-5136-4be5-846b-4a93eb4c576 || {
    echo Failed
    EXITVAL=1
}

exit $EXITVAL