#! /bin/bash

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


mkdir oblib/data
cd oblib/data
git clone --branch 2020-04-01 https://github.com/SunSpecOrangeButton/solar-taxonomy.git
cd solar-taxonomy
rm SolarTaxonomyMaster.xlsx
mkdir external
curl http://xbrl.fasb.org/us-gaap/2017/elts/us-gaap-2017-01-31.xsd > external/us-gaap-2017-01-31.xsd
curl https://xbrl.sec.gov/dei/2018/dei-2018-01-31.xsd > external/dei-2018-01-31.xsd
curl https://www.xbrl.org/utr/utr.xml > external/utr.xml
