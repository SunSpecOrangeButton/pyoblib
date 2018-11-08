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

# This uses pdoc to create text based documentation.  It is very basic
# and it likely  could be replaced with an HTML based documentation
# generator.  To run this script "pip install pdoc" must be issued first.

export PYTHONPATH=`pwd`/oblib

# pdoc --html --overwrite --html-dir=out src
# cp -r out/oblib docs/oblib

pdoc /oblib/identifier.py
echo
echo

pdoc /oblib/taxonomy.py
echo
echo

pdoc /oblib/taxonomy_semantic.py
echo
echo

pdoc /oblib/taxonomy_types.py
echo
echo

pdoc /oblib/taxonomy_units.py
echo
echo

pdoc /oblib/taxonomy_misc.py
