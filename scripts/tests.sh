#! /bin/bash

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

echo Testing

export PYTHONPATH=`pwd`/src:`pwd`/tests

EXITVAL=0

python -m unittest test_identifier || {
    EXITVAL=1
}

python -m unittest test_taxonomy || {
    EXITVAL=1
}

python -m unittest test_taxonomy_semantic || {
    EXITVAL=1
}

python -m unittest test_taxonomy_types || {
    EXITVAL=1
}

python -m unittest test_taxonomy_misc || {
    EXITVAL=1
}

python -m unittest test_taxonomy_units || {
    EXITVAL=1
}

python -m unittest test_validator || {
    EXITVAL=1
}

exit $EXITVAL
