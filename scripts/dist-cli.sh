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

# TODO: Usage of ../solar-taxonomy works on the first run of the compiled
# cli but does not clean up at the end of the run.  Subsequent runs 
# produce warnings but still function.  In order to correct the behavior
# remove .. from the path.  This will require coding changes to find the
# correct placement of solar-taxonomy.

export PYTHONPATH=`pwd`/src/obcore
pyinstaller --add-data ../solar-taxonomy:../solar-taxonomy --clean --onefile src/obcli/cli.py
