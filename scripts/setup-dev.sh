#! /bin/bash

# Copyright 2018 SunSpec Alliance

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
git clone https://github.com/SunSpecOrangeButton/solar-taxonomy.git
mkdir solar-taxonomy/external
curl http://xbrl.fasb.org/us-gaap/2017/elts/us-gaap-2017-01-31.xsd > oblib/data/solar-taxonomy/external/us-gaap-2017-01-31.xsd
curl https://xbrl.sec.gov/dei/2018/dei-2018-01-31.xsd > oblib/data/solar-taxonomy/external/dei-2018-01-31.xsd
curl https://www.xbrl.org/utr/utr.xml > oblib/data/solar-taxonomy/external/utr.xml
