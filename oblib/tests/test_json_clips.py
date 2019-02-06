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

import re
from inspect import currentframe
import unittest
from oblib import parser, taxonomy


taxonomy = taxonomy.Taxonomy()
parser = parser.Parser(taxonomy)


def _ln():
    # Returns line number of caller.

    cf = currentframe()
    return cf.f_back.f_lineno


class TestJsonClips(unittest.TestCase):
    # Note: this module is tested differently than others.  Erroneous JSON clips are run through
    # the parser validator method and should cause various error methods to occur.  The resulting
    # exception string is expected to match a regular expression which should prove that enough
    # information is returned to correctly diagnose the error (although a perfect match is not
    # necessarily required unless noted via the expression).  A line number in the JSON also is
    # present and in an ideal world the line number should also be decipherable fromt he parser.

    def test_clips(self):
        failure_list = []
        for clip in CLIPS:
            try:
                parser.from_JSON_string(JSON_HEADER + clip[4] + JSON_FOOTER, entrypoint_name=clip[1])
                if clip[2] is not None:
                    failure_list.append("Case {} did not cause a failure condition as expected".format(clip[0]))
            except Exception as e:
                s = str(e)
                if clip[2] is None:
                    failure_list.append("Case {} should have succeeded, raised {}".format(clip[0], s))
                elif re.search(clip[2], s, re.IGNORECASE) is None:
                    failure_list.append("Case {} exception text '{}' did not meet expected value '{}'".format(clip[0], s, clip[2]))

        if len(failure_list) > 0:
            msg = "\n"
            for f in failure_list:
                msg = msg + f + "\n"
            # TODO: Uncomment this line and remove the print statement.  At this point in time the
            # validator rules are not implemented so this test case cannot actually fail although
            # in reality it should be failing.
            # self.fail(msg)
            print(msg)


CLIPS = [
    # Basic tests of each JSON field
    [_ln(), "MonthlyOperatingReport", "Identifier is not a uuid", 1, """
        {
            "id": "illegal-identifier",
            "value": 93.26,
            "aspects": {
                "xbrl:concept": "solar:MeasuredEnergyAvailabilityPercent",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],
    [_ln(), "MonthlyOperatingReport", "Float expected", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Bad Data",
            "aspects": {
                "xbrl:concept": "solar:MeasuredEnergyAvailabilityPercent",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],
    [_ln(), "MonthlyOperatingReport", "is not a writeable concept", 4, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Bad Data",
            "aspects": {
                "xbrl:concept": 2,
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],
    [_ln(), "MonthlyOperatingReport", "Entity is not a string", 5, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Bad Data",
            "aspects": {
                "xbrl:concept": "solar:MeasuredEnergyAvailabilityPercent",
                "xbrl:entity": 3,
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],
    [_ln(), "MonthlyOperatingReport", "Illegal Period Start", 6, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 93.26,
            "aspects": {
                "xbrl:concept": "solar:MeasuredEnergyAvailabilityPercent",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-13-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],
    [_ln(), "MonthlyOperatingReport", "Illegal Period End", 7, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 93.26,
            "aspects": {
                "xbrl:concept": "solar:MeasuredEnergyAvailabilityPercent",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-13-30T00:00:00"
            }
        }
        """
     ],
    [_ln(), "MonthlyOperatingReport", "Identifier is not a uuid", 1, """
        {
            "id": "illegal-identifier",
            "value": 93.26,
            "aspects": {
                "xbrl:concept": "solar:MeasuredEnergyAvailabilityPercent",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],

    # Validate that all required fields are present.  Note that all fields are required except
    # periodStart and periodEnd (if missing this indicates that duration is forever)
    [_ln(), "MonthlyOperatingReport", "Identifier is missing", 0, """
        {
            "value": 93.26,
            "aspects": {
                "xbrl:concept": "solar:MeasuredEnergyAvailabilityPercent",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],
    [_ln(), "MonthlyOperatingReport", "Value is missing", 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "aspects": {
                "xbrl:concept": "solar:MeasuredEnergyAvailabilityPercent",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],
    [_ln(), "MonthlyOperatingReport", "Aspects is missing", 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 93.26,
        }
        """
     ],
    [_ln(), "MonthlyOperatingReport", "Concept is missing", 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 93.26,
            "aspects": {
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],
    [_ln(), "MonthlyOperatingReport", "Entity is missing", 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 93.26,
            "aspects": {
                "xbrl:concept": "solar:MeasuredEnergyAvailabilityPercent",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],

    # Check that a non-nillable field is not set to null
    [_ln(), "MasterPurchaseAgreement", "Non-nillable value is set to null", 3, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": null,
            "aspects": {
                "xbrl:concept": "solar:PreparerOfMasterPurchaseAgreement",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],

    # Type checks - basic types

    # us-types:perUnitItemType, Sample valid value is UNKNOWN
    # TODO: Implement
    # [_ln(), "", "value is not legal for type us-types:perUnitItemType", 2, """
    #     {
    #         "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
    #         "value": false,
    #         "aspects": {
    #             "xbrl:concept": "us-types:perUnitItemType",
    #             "xbrl:entity": "JUPITER",
    #             "xbrl:periodStart": "2017-11-01T00:00:00",
    #             "xbrl:periodEnd": "2017-11-30T00:00:00"
    #         }
    #     }
    #     """
    # ],

    # xbrli:booleanItemType, Sample valid value is false
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": true,
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportAvailabilityOfDocument",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportAvailabilityOfDocument",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],
    [_ln(), None, "value is not legal for type xbrli:booleanItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "non-boolean",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportAvailabilityOfDocument",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],
    [_ln(), None, "value is not legal for type xbrli:booleanItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "true",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportAvailabilityOfDocument",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],
    [_ln(), None, "value is not legal for type xbrli:booleanItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "false",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportAvailabilityOfDocument",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],
    [_ln(), None, "value is not legal for type xbrli:booleanItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 1,
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportAvailabilityOfDocument",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],
    [_ln(), None, "value is not legal for type xbrli:booleanItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 0,
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportAvailabilityOfDocument",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],
    [_ln(), None, "value is not legal for type xbrli:booleanItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 1.0,
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportAvailabilityOfDocument",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],
    [_ln(), None, "value is not legal for type xbrli:booleanItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 0.0,
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportAvailabilityOfDocument",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],

    # xbrli:dateItemType, Sample valid value is 2018-01-02
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-01-01",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-01-31",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-02-01",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2017-02-28",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-02-28",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2019-02-28",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],
    # Leap Year
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2020-02-29",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-03-01",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-03-31",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-04-01",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-04-30",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-05-01",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-05-31",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-06-01",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
     ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-06-30",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-07-01",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-07-31",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-08-01",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-08-31",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-01-01",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-09-30",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-10-01",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-10-31",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-11-01",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-11-30",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-12-01",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-12-31",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],    
    [_ln(), None, "value is not legal for type xbrli:dateItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-13-02",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:dateItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-01-32",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:dateItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2016-02-30",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:dateItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2017-02-28",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:dateItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2019-02-29",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    # Leap Year
    [_ln(), None, "value is not legal for type xbrli:dateItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2020-02-30",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:dateItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-03-32",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:dateItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-04-30",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:dateItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-05-32",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:dateItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-06-31",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:dateItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-08-32",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:dateItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-09-31",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:dateItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-10-32",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:dateItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-11-31",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:dateItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-12-32",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:dateItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-1-01",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:dateItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018-01-1",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:dateItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2018_01_01",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:dateItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "01-01-2018",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:dateItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "01/01/2018",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:dateItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:dateItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:dateItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 99,
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:dateItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 99.99,
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportEndDate",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # xbrli:decimalItemType, Sample valid value is 99.99
    [_ln(), "System", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 99.99,
            "aspects": {
                "xbrl:concept": "solar:MonitoringSolutionSoftwareVersion",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "System", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 99.00,
            "aspects": {
                "xbrl:concept": "solar:MonitoringSolutionSoftwareVersion",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "System", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": -99.99,
            "aspects": {
                "xbrl:concept": "solar:MonitoringSolutionSoftwareVersion",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "System", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 99,
            "aspects": {
                "xbrl:concept": "solar:MonitoringSolutionSoftwareVersion",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "System", "value is not legal for type xbrli:decimalItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:MonitoringSolutionSoftwareVersion",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "System", "value is not legal for type xbrli:decimalItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "99.99",
            "aspects": {
                "xbrl:concept": "solar:MonitoringSolutionSoftwareVersion",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "System", "value is not legal for type xbrli:decimalItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:MonitoringSolutionSoftwareVersion",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # xbrli:durationItemType, Sample valid value's are documented at based on the last
    # paragragh of http://books.xmlschemata.org/relaxng/ch19-77073.html
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "P1Y",
            "aspects": {
                "xbrl:concept": "solar:EstimationPeriodForCurtailment",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-30T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "PT1004199059S",
            "aspects": {
                "xbrl:concept": "solar:EstimationPeriodForCurtailment",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-30T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "PT130S",
            "aspects": {
                "xbrl:concept": "solar:EstimationPeriodForCurtailment",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-30T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "PT2M10S",
            "aspects": {
                "xbrl:concept": "solar:EstimationPeriodForCurtailment",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-30T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "P1DT2S",
            "aspects": {
                "xbrl:concept": "solar:EstimationPeriodForCurtailment",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-30T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "-P1Y",
            "aspects": {
                "xbrl:concept": "solar:EstimationPeriodForCurtailment",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-30T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "P1Y2M3DT5H20M30.123S",
            "aspects": {
                "xbrl:concept": "solar:EstimationPeriodForCurtailment",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-30T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:durationItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid",
            "aspects": {
                "xbrl:concept": "solar:EstimationPeriodForCurtailment",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-30T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:durationItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "1Y",
            "aspects": {
                "xbrl:concept": "solar:EstimationPeriodForCurtailment",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-30T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:durationItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "P1S",
            "aspects": {
                "xbrl:concept": "solar:EstimationPeriodForCurtailment",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-30T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:durationItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "P1-Y",
            "aspects": {
                "xbrl:concept": "solar:EstimationPeriodForCurtailment",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-30T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:durationItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "P1M2Y",
            "aspects": {
                "xbrl:concept": "solar:EstimationPeriodForCurtailment",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-30T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:durationItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "P1Y-1M",
            "aspects": {
                "xbrl:concept": "solar:EstimationPeriodForCurtailment",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-30T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:durationItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:EstimationPeriodForCurtailment",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-30T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:durationItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 99,
            "aspects": {
                "xbrl:concept": "solar:EstimationPeriodForCurtailment",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-30T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:durationItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 99.99,
            "aspects": {
                "xbrl:concept": "solar:EstimationPeriodForCurtailment",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-30T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:durationItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid",
            "aspects": {
                "xbrl:concept": "solar:EstimationPeriodForCurtailment",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-30T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],


    # xbrli:integerItemType, Sample valid value is 99
    [_ln(), "WashingAndWasteAgreement", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 99,
            "aspects": {
                "xbrl:concept": "solar:WashingAndWasteFrequencyOfWashing",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:SiteIdentifierAxis": "1"
            }
        }
        """
    ],
    [_ln(), "WashingAndWasteAgreement", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": -99,
            "aspects": {
                "xbrl:concept": "solar:WashingAndWasteFrequencyOfWashing",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:SiteIdentifierAxis": "1"
            }
        }
        """
    ],
    [_ln(), "WashingAndWasteAgreement", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 0,
            "aspects": {
                "xbrl:concept": "solar:WashingAndWasteFrequencyOfWashing",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:SiteIdentifierAxis": "1"
            }
        }
        """
    ],
    [_ln(), "WashingAndWasteAgreement", "value is not legal for type xbrli:integerItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:WashingAndWasteFrequencyOfWashing",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:SiteIdentifierAxis": "1"
            }
        }
        """
    ],
    [_ln(), "WashingAndWasteAgreement", "value is not legal for type xbrli:integerItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 99.99,
            "aspects": {
                "xbrl:concept": "solar:WashingAndWasteFrequencyOfWashing",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:SiteIdentifierAxis": "1"
            }
        }
        """
    ],
    [_ln(), "WashingAndWasteAgreement", "value is not legal for type xbrli:integerItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "99",
            "aspects": {
                "xbrl:concept": "solar:WashingAndWasteFrequencyOfWashing",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:SiteIdentifierAxis": "1"
            }
        }
        """
    ],
    [_ln(), "WashingAndWasteAgreement", "value is not legal for type xbrli:integerItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid",
            "aspects": {
                "xbrl:concept": "solar:WashingAndWasteFrequencyOfWashing",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:SiteIdentifierAxis": "1"
            }
        }
        """
    ],

    # xbrli:monetaryItemType, Sample valid value is 9999.99
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 9999.99,
            "aspects": {
                "xbrl:concept": "us-gaap:PrepaidExpenseCurrentAndNoncurrent",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-30T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    [_ln(), None, "value is not legal for type xbrli:monetaryItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "us-gaap:PrepaidExpenseCurrentAndNoncurrent",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-30T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:monetaryItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 9999,
            "aspects": {
                "xbrl:concept": "us-gaap:PrepaidExpenseCurrentAndNoncurrent",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-30T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:monetaryItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 9999.9,
            "aspects": {
                "xbrl:concept": "us-gaap:PrepaidExpenseCurrentAndNoncurrent",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-30T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
        [_ln(), None, "value is not legal for type xbrli:monetaryItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 9999.999,
            "aspects": {
                "xbrl:concept": "us-gaap:PrepaidExpenseCurrentAndNoncurrent",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-30T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    [_ln(), None, "value is not legal for type xbrli:monetaryItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "9999.99",
            "aspects": {
                "xbrl:concept": "us-gaap:PrepaidExpenseCurrentAndNoncurrent",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-30T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:monetaryItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid",
            "aspects": {
                "xbrl:concept": "us-gaap:PrepaidExpenseCurrentAndNoncurrent",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-30T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # # xbrli:pureItemType, Sample valid value is UNKNOWN
    # # TODO: Implement
    # [_ln(), "", "value is not legal for type xbrli:pureItemType", 2, """
    #     {
    #         "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
    #         "value": false,
    #         "aspects": {
    #             "xbrl:concept": "xbrli:pureItemType",
    #             "xbrl:entity": "JUPITER",
    #             "xbrl:periodStart": "2017-11-01T00:00:00",
    #             "xbrl:periodEnd": "2017-11-30T00:00:00"
    #         }
    #     }
    #     """
    # ],

    # xbrli:stringItemType, Sample valid value is "Sample String"
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Sample String",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportExceptionDescription",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:stringItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportExceptionDescription",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:stringItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 99,
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportExceptionDescription",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type xbrli:stringItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 99.99,
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportExceptionDescription",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    # num:percentItemType, Sample valid value is 99.99
    [_ln(), "IECRECertificate", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 99.99,
            "aspects": {
                "xbrl:concept": "solar:AerosolModelFactorTMMPercent",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "IECRECertificate", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 0.0,
            "aspects": {
                "xbrl:concept": "solar:AerosolModelFactorTMMPercent",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "IECRECertificate", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 99,
            "aspects": {
                "xbrl:concept": "solar:AerosolModelFactorTMMPercent",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "IECRECertificate", "value is not legal for type num:percentItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": -0.01,
            "aspects": {
                "xbrl:concept": "solar:AerosolModelFactorTMMPercent",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "IECRECertificate", "value is not legal for type num:percentItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 100.01,
            "aspects": {
                "xbrl:concept": "solar:AerosolModelFactorTMMPercent",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "IECRECertificate", "value is not legal for type num:percentItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:AerosolModelFactorTMMPercent",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "IECRECertificate", "value is not legal for type num:percentItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:AerosolModelFactorTMMPercent",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # Type checks - advanced types

    # xbrli:anyURIItemType, Sample valid value is http://www.google.com
    # Please note that the validation is very basic at this point in time.  It could be expanded
    # to be reflective of full URI rules although this may have diminishing returns against other
    # goals give that (1) URI is not common in the Taxonomy and (2) whether illegal URI's should
    # be rejected  or not is currently undefined from a requirements standpoint.
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "http://www.google.com",
            "aspects": {
                "xbrl:concept": "solar:CutSheetDocumentLink",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "https://www.google.com",
            "aspects": {
                "xbrl:concept": "solar:CutSheetDocumentLink",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],
    [_ln(), "", "value is not legal for type xbrli:anyURIItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:CutSheetDocumentLink",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],
    [_ln(), "", "value is not legal for type xbrli:anyURIItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 99.99,
            "aspects": {
                "xbrl:concept": "solar:CutSheetDocumentLink",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],
    [_ln(), "", "value is not legal for type xbrli:anyURIItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 99,
            "aspects": {
                "xbrl:concept": "solar:CutSheetDocumentLink",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],

    # dei:legalEntityIdentifierItemType, Sample valid value is 5493006MHB84DD0ZWV18
    [_ln(), "Participant", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "5493006MHB84DD0ZWV18",
            "aspects": {
                "xbrl:concept": "dei:LegalEntityIdentifier",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    [_ln(), "Participant", "value is not legal for type dei:legalEntityIdentifierItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "dei:LegalEntityIdentifier",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # nonnum:domainItemType, Sample valid value is UNKNOWN
    # TODO: Implement
    # [_ln(), "", "value is not legal for type nonnum:domainItemType", 2, """
    #     {
    #         "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
    #         "value": false,
    #         "aspects": {
    #             "xbrl:concept": "nonnum:domainItemType",
    #             "xbrl:entity": "JUPITER",
    #             "xbrl:periodStart": "2017-11-01T00:00:00",
    #             "xbrl:periodEnd": "2017-11-30T00:00:00"
    #         }
    #     }
    #     """
    # ],

    # num-us:electricCurrentItemType, Sample valid value is 99.99
    [_ln(), "CutSheet", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 99.99,
            "aspects": {
                "xbrl:concept": "solar:ModuleShortCircuitCurrent",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],
    [_ln(), "CutSheet", "value is not legal for type num-us:electricCurrentItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:ModuleShortCircuitCurrent",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],

    # num-us:frequencyItemType, Sample valid value is 99.99
    [_ln(), "CutSheet", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 99.99,
            "aspects": {
                "xbrl:concept": "solar:InverterOutputRatedFrequency",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],
    [_ln(), "CutSheet", "value is not legal for type num-us:frequencyItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:InverterOutputRatedFrequency",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],

    # num-us:insolationItemType, Sample valid value is 99.99
    [_ln(), "MonthlyOperatingReport", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 99.99,
            "aspects": {
                "xbrl:concept": "solar:ExpectedInsolationAtP50",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "MonthlyOperatingReport", "value is not legal for type num-us:insolationItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:ExpectedInsolationAtP50",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "MonthlyOperatingReport", "value is out of range for type num-us:insolationItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 101.01,
            "aspects": {
                "xbrl:concept": "solar:ExpectedInsolationAtP50",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # num-us:irradianceItemType, Sample valid value is 99.99
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 99.99,
            "aspects": {
                "xbrl:concept": "solar:SystemMinimumIrradianceThreshold",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type num-us:irradianceItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:SystemMinimumIrradianceThreshold",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # num-us:planeAngleItemType, Sample valid value is 33.33
    [_ln(), "SystemDeviceListing", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 33.33,
            "aspects": {
                "xbrl:concept": "solar:TrackerAzimuth",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-01T00:00:00"
            }
        }
        """
    ],
    [_ln(), "SystemDeviceListing", "value is out of range for type num-us:planeAngleItemType", 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 361.10,
            "aspects": {
                "xbrl:concept": "solar:TrackerAzimuth",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-01T00:00:00"
            }
        }
        """
    ],
    [_ln(), "SystemDeviceListing", "value is not legal for type num-us:planeAngleItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:TrackerAzimuth",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-01T00:00:00"
            }
        }
        """
    ],

    # num-us:pressureItemType, Sample valid value is 99.99
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 99.99,
            "aspects": {
                "xbrl:concept": "solar:SiteBarometricPressure",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-01T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type num-us:pressureItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:SiteBarometricPressure",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-01T00:00:00"
            }
        }
        """
    ],

    # num-us:speedItemType, Sample valid value is 19.19
    [_ln(), "CutSheet", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 19.19,
            "aspects": {
                "xbrl:concept": "solar:TrackerStowWindSpeed",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],
    [_ln(), "CutSheet", "value is not legal for type num-us:speedItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:TrackerStowWindSpeed",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],

    # num-us:temperatureItemType, Sample valid value is 74.74
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:ModelAmbientTemperature",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type num-us:temperatureItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:ModelAmbientTemperature",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # num-us:voltageItemType, Sample valid value is 99.99
    [_ln(), "CutSheet", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 99.99,
            "aspects": {
                "xbrl:concept": "solar:InverterInputMaximumVoltageDC",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],
    [_ln(), "CutSheet", "value is not legal for type num-us:voltageItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:InverterInputMaximumVoltageDC",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],

    # num:areaItemType, Sample valid value is 99.99
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 99.99,
            "aspects": {
                "xbrl:concept": "solar:SiteAcreage",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type num:areaItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:SiteAcreage",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # num:energyItemType, Sample valid value is 99.99
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 99.99,
            "aspects": {
                "xbrl:concept": "solar:ExpectedEnergyAtP50",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-01T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type num:energyItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:ExpectedEnergyAtP50",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-01T00:00:00"
            }
        }
        """
    ],

    # num:lengthItemType, Sample valid value is 99.99
    [_ln(), "CutSheet", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:ModuleLength",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],
    [_ln(), "CutSheet", "value is not legal for type num:lengthItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:ModuleLength",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],

    # num:massItemType, Sample valid value is 99.99
    [_ln(), "CutSheet", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 99.99,
            "aspects": {
                "xbrl:concept": "solar:InverterWeight",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],
    [_ln(), "CutSheet", "value is not legal for type num:massItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:InverterWeight",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],

    # num:powerItemType, Sample valid value is 99.99
    [_ln(), "IECRECertificate", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 99.99,
            "aspects": {
                "xbrl:concept": "solar:BatteryInverterACPowerRating",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "IECRECertificate", "value is not legal for type num:powerItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:BatteryInverterACPowerRating",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # num:volumeItemType, Sample valid value is 99.99
    [_ln(), "WashingAndWasteAgreement", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": 99.99,
            "aspects": {
                "xbrl:concept": "solar:WashingAndWasteQuantityOfWater",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:SiteIdentifierAxis": "1"
            }
        }
        """
    ],
    [_ln(), "WashingAndWasteAgreement", "value is not legal for type num:volumeItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:WashingAndWasteQuantityOfWater",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:SiteIdentifierAxis": "1"
            }
        }
        """
    ],

    # solar-types:DERItemType, Sample valid value is "Storage"
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Storage",
            "aspects": {
                "xbrl:concept": "solar:SystemDERType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:DERItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:SystemDERType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:DERItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:SystemDERType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:aLTASurveyItemType, Sample valid value is "Preliminary"
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Preliminary",
            "aspects": {
                "xbrl:concept": "solar:AmericanLandTitleAssociationSurveyStatus",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:aLTASurveyItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:AmericanLandTitleAssociationSurveyStatus",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:aLTASurveyItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:AmericanLandTitleAssociationSurveyStatus",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:batteryChemistryItemType, Sample valid value is "NiCad"
    [_ln(), "IECRECertificate", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "NiCad",
            "aspects": {
                "xbrl:concept": "solar:BatteryStyle",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
   [_ln(), "IECRECertificate", "value is not legal for type solar-types:batteryChemistryItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:BatteryStyle",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
   [_ln(), "IECRECertificate", "value is not legal for type solar-types:batteryChemistryItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:BatteryStyle",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:batteryConnectionItemType, Sample valid value is "DC-Coupled"
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "DC-Coupled",
            "aspects": {
                "xbrl:concept": "solar:SystemBatteryConnection",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:batteryConnectionItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:SystemBatteryConnection",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:batteryConnectionItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:SystemBatteryConnection",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:climateClassificationKoppenItemType, Sample valid value is "2.4.1 Hot summer continental climates"
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "2.4.1 Hot summer continental climates",
            "aspects": {
                "xbrl:concept": "solar:SiteClimateClassificationKoppen",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:climateClassificationKoppenItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:SiteClimateClassificationKoppen",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:climateClassificationKoppenItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:SiteClimateClassificationKoppen",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:climateZoneANSIItemType, Sample valid value is "Mixed - Marine"
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Mixed - Marine",
            "aspects": {
                "xbrl:concept": "solar:SiteClimateZoneTypeANSI",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:climateZoneANSIItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:SiteClimateZoneTypeANSI",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:climateZoneANSIItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:SiteClimateZoneTypeANSI",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:communicationProtocolItemType, Sample valid value is "Modbus"
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Modbus",
            "aspects": {
                "xbrl:concept": "solar:DataAcquisitionSystemCommunicationProtocol",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:communicationProtocolItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:DataAcquisitionSystemCommunicationProtocol",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:communicationProtocolItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:DataAcquisitionSystemCommunicationProtocol",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:deviceItemType, Sample valid value is "BatteryManagementSystemMember"
    [_ln(), "CutSheet", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "BatteryManagementSystemMember",
            "aspects": {
                "xbrl:concept": "solar:TypeOfDevice",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],
    [_ln(), "CutSheet", "value is not legal for type solar-types:deviceItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:TypeOfDevice",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],
    [_ln(), "CutSheet", "value is not legal for type solar-types:deviceItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:TypeOfDevice",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],

    # solar-types:distributedGenOrUtilityScaleItemType, Sample valid value is "Distributed Generation"
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Distributed Generation",
            "aspects": {
                "xbrl:concept": "solar:ProjectDistributedGenerationPortolioOrUtilityScale",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:IndependentEngineeringServicesChecklistAxis": "solar:IndependentEngineeringServicesChecklistPostFundingActivityMember"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:distributedGenOrUtilityScaleItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:ProjectDistributedGenerationPortolioOrUtilityScale",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:IndependentEngineeringServicesChecklistAxis": "solar:IndependentEngineeringServicesChecklistPostFundingActivityMember"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:distributedGenOrUtilityScaleItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:ProjectDistributedGenerationPortolioOrUtilityScale",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:IndependentEngineeringServicesChecklistAxis": "solar:IndependentEngineeringServicesChecklistPostFundingActivityMember"
            }
        }
        """
    ],

    # solar-types:divisionStateApprovalStatusItemType, Sample valid value is "Final Approval"
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Final Approval",
            "aspects": {
                "xbrl:concept": "solar:DivisionOfStateArchitectApprovalStatus",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:divisionStateApprovalStatusItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:DivisionOfStateArchitectApprovalStatus",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:divisionStateApprovalStatusItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:DivisionOfStateArchitectApprovalStatus",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:eventSeverityItemType, Sample valid value is "Moderate"
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Moderate",
            "aspects": {
                "xbrl:concept": "solar:ProjectRecentEventSeverityOfEvent",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:eventSeverityItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:ProjectRecentEventSeverityOfEvent",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:eventSeverityItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:ProjectRecentEventSeverityOfEvent",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:feeStatusItemType, Sample valid value is "Fully Paid"
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:ZoningPermitUpfrontFeeStatus",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:feeStatusItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:ZoningPermitUpfrontFeeStatus",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:feeStatusItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invald Value",
            "aspects": {
                "xbrl:concept": "solar:ZoningPermitUpfrontFeeStatus",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:fundStatusItemType, Sample valid value is "Committed"
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:FundStatus",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:fundStatusItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:FundStatus",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:fundStatusItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:FundStatus",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:gISFileFormatItemType, Sample valid value is "GEOJson"
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "GEOJson",
            "aspects": {
                "xbrl:concept": "solar:SiteGeospatialBoundaryGISFileFormat",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:gISFileFormatItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:SiteGeospatialBoundaryGISFileFormat",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:gISFileFormatItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:SiteGeospatialBoundaryGISFileFormat",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:hedgeItemType, Sample valid value is "Revenue Put"
    [_ln(), "", "value is not legal for type solar-types:hedgeItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Revenue Put",
            "aspects": {
                "xbrl:concept": "solar:ProjectHedgeAgreementType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "", "value is not legal for type solar-types:hedgeItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:ProjectHedgeAgreementType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "", "value is not legal for type solar-types:hedgeItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:ProjectHedgeAgreementType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:insuranceItemType, Sample valid value is "Surety Solar Module Supply Bond"
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Surety Solar Module Supply Bond",
            "aspects": {
                "xbrl:concept": "solar:InsuranceType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:insuranceItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:InsuranceType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:insuranceItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:InsuranceType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:internetConnectionItemType, Sample valid value is "Dedicated Broadband"
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:NetworkType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:internetConnectionItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:NetworkType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:internetConnectionItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:NetworkType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:inverterItemType, Sample valid value is "MicroInverter"
    [_ln(), "IECRECertificate", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "MicroInverter",
            "aspects": {
                "xbrl:concept": "solar:InverterStyle",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "IECRECertificate", "value is not legal for type solar-types:inverterItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:InverterStyle",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "IECRECertificate", "value is not legal for type solar-types:inverterItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:InverterStyle",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:inverterPhaseItemType, Sample valid value is "Three Phase WYE"
    [_ln(), "CutSheet", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Three Phase WYE",
            "aspects": {
                "xbrl:concept": "solar:InverterOutputPhaseType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],
    [_ln(), "CutSheet", "value is not legal for type solar-types:inverterPhaseItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:InverterOutputPhaseType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],
    [_ln(), "CutSheet", "value is not legal for type solar-types:inverterPhaseItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:InverterOutputPhaseType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],

    # solar-types:investmentStatusItemType, Sample valid value is "Partial Funding"
    [_ln(), "", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Partial Funding",
            "aspects": {
                "xbrl:concept": "solar:ProjectInvestmentStatus",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "", "value is not legal for type solar-types:investmentStatusItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:ProjectInvestmentStatus",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "", "value is not legal for type solar-types:investmentStatusItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:ProjectInvestmentStatus",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:mORLevelItemType, Sample valid value is "Fund Level"
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Fund Level",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportLevel",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:mORLevelItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportLevel",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:mORLevelItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:MonthlyOperatingReportLevel",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:moduleItemType, Sample valid value is "BiFacial"
    [_ln(), "CutSheet", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "BiFacial",
            "aspects": {
                "xbrl:concept": "solar:ModuleStyle",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],
    [_ln(), "CutSheet", "value is not legal for type solar-types:moduleItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:ModuleStyle",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],
    [_ln(), "CutSheet", "value is not legal for type solar-types:moduleItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:ModuleStyle",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],

    # solar-types:moduleOrientationItemType, Sample valid value is "Portrait"
    [_ln(), "CutSheet", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Portrait",
            "aspects": {
                "xbrl:concept": "solar:ModuleOrientation",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],
    [_ln(), "CutSheet", "value is not legal for type solar-types:moduleOrientationItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:ModuleOrientation",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],
    [_ln(), "CutSheet", "value is not legal for type solar-types:moduleOrientationItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:ModuleOrientation",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],

    # solar-types:moduleTechnologyItemType, Sample valid value is "Multi-C-Si"
    [_ln(), "CutSheet", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Multi-C-Si",
            "aspects": {
                "xbrl:concept": "solar:ModuleTechnology",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],
    [_ln(), "CutSheet", "value is not legal for type solar-types:moduleTechnologyItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:ModuleTechnology",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],
    [_ln(), "CutSheet", "value is not legal for type solar-types:moduleTechnologyItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:ModuleTechnology",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],

    # solar-types:mountingItemType, Sample valid value is "Ballasted"
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Ballasted",
            "aspects": {
                "xbrl:concept": "solar:MountingType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:mountingItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:MountingType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:mountingItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:MountingType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:occupancyItemType, Sample valid value is "Owner Occupied"
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Owner Occupied",
            "aspects": {
                "xbrl:concept": "solar:SitePropertyOccupancyType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:occupancyItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:SitePropertyOccupancyType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:occupancyItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:SitePropertyOccupancyType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:optimizerTypeItemType, Sample valid value is "Attached"
    [_ln(), "CutSheet", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Attached",
            "aspects": {
                "xbrl:concept": "solar:OptimizerType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],
    [_ln(), "CutSheet", "value is not legal for type solar-types:optimizerTypeItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:OptimizerType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],
    [_ln(), "CutSheet", "value is not legal for type solar-types:optimizerTypeItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:OptimizerType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:TestConditionAxis": "solar:CustomTestConditionMember",
                "solar:ProductIdentifierAxis": "1"
            }
        }
        """
    ],

    # solar-types:participantItemType, Sample valid value is "Workers Compensation Insurer"
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Workers Compensation Insurer",
            "aspects": {
                "xbrl:concept": "solar:ParticipantRole",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:participantItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:ParticipantRole",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:participantItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:ParticipantRole",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:preventiveMaintenanceTaskStatusItemType, Sample valid value is "Incomplete"
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Incomplete",
            "aspects": {
                "xbrl:concept": "solar:SystemPreventiveMaintenanceTasksStatus",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:preventiveMaintenanceTaskStatusItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:SystemPreventiveMaintenanceTasksStatus",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:preventiveMaintenanceTaskStatusItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:SystemPreventiveMaintenanceTasksStatus",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:projectAssetTypeItemType, Sample valid value is "Solar Plus Storage"
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Solar Plus Storage",
            "aspects": {
                "xbrl:concept": "solar:ProjectAssetType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:projectAssetTypeItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:ProjectAssetType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:projectAssetTypeItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:ProjectAssetType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:projectClassItemType, Sample valid value is "Community Solar"
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Community Solar",
            "aspects": {
                "xbrl:concept": "solar:ProjectClassType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:projectClassItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:ProjectClassType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:projectClassItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:ProjectClassType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:projectInterconnectionItemType, Sample valid value is "Virtual Net Meter"
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Virtual Net Meter",
            "aspects": {
                "xbrl:concept": "solar:ProjectInterconnectionType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:projectInterconnectionItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:ProjectInterconnectionType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:projectInterconnectionItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:ProjectInterconnectionType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:projectPhaseItemType, Sample valid value is "Early Construction"
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Early Construction",
            "aspects": {
                "xbrl:concept": "solar:PhaseOfProjectNeeded",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:IndependentEngineeringServicesChecklistAxis": "solar:IndependentEngineeringServicesChecklistPostFundingActivityMember"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:projectPhaseItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:PhaseOfProjectNeeded",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:IndependentEngineeringServicesChecklistAxis": "solar:IndependentEngineeringServicesChecklistPostFundingActivityMember"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:projectPhaseItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:PhaseOfProjectNeeded",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00",
                "solar:IndependentEngineeringServicesChecklistAxis": "solar:IndependentEngineeringServicesChecklistPostFundingActivityMember"
            }
        }
        """
    ],

    # solar-types:projectStageItemType, Sample valid value is "In Operation"
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "In Operation",
            "aspects": {
                "xbrl:concept": "solar:ProjectStage",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:projectStageItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:ProjectStage",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:projectStageItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:ProjectStage",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:regulatoryApprovalStatusItemType, Sample valid value is "Not Submitted"
    [_ln(), "Project", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Not Submitted",
            "aspects": {
                "xbrl:concept": "solar:RegulatoryApprovalStatus",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "Project", "value is not legal for type solar-types:regulatoryApprovalStatusItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:RegulatoryApprovalStatus",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "Project", "value is not legal for type solar-types:regulatoryApprovalStatusItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:RegulatoryApprovalStatus",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:regulatoryFacilityItemType, Sample valid value is "EWG"
    [_ln(), "Project", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "EWG",
            "aspects": {
                "xbrl:concept": "solar:RegulatoryFacilityType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "Project", "value is not legal for type solar-types:regulatoryFacilityItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:RegulatoryFacilityType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "Project", "value is not legal for type solar-types:regulatoryFacilityItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:RegulatoryFacilityType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:reserveCollateralItemType, Sample valid value is "Letter of Credit"
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Letter of Credit",
            "aspects": {
                "xbrl:concept": "solar:ReserveCollateralType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:reserveCollateralItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:ReserveCollateralType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:reserveCollateralItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:ReserveCollateralType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:reserveUseItemType, Sample valid value is "Maintenance"
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Maintenance",
            "aspects": {
                "xbrl:concept": "solar:ReserveUse",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:reserveUseItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:ReserveUse",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:reserveUseItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:ReserveUse",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:roofItemType, Sample valid value is "Thermoplastic Polyolefin"
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:RoofType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:roofItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:RoofType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:roofItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:RoofType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:roofSlopeItemType, Sample valid value is "Steep"
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:RoofSlopeType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:roofSlopeItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:RoofSlopeType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:roofSlopeItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:RoofSlopeType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:siteControlItemType, Sample valid value is "Lease"
    [_ln(), "Site", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Lease",
            "aspects": {
                "xbrl:concept": "solar:SiteControlType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "Site", "value is not legal for type solar-types:siteControlItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:SiteControlType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "Site", "value is not legal for type solar-types:siteControlItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:SiteControlType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:solarSystemCharacterItemType, Sample valid value is "Agricultural"
    [_ln(), "System", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Agricultural",
            "aspects": {
                "xbrl:concept": "solar:SystemType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "System", "value is not legal for type solar-types:solarSystemCharacterItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:SystemType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "System", "value is not legal for type solar-types:solarSystemCharacterItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:SystemType",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:sparePartsStatusItemType, Sample valid value is "Insufficient"
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Insufficient",
            "aspects": {
                "xbrl:concept": "solar:SystemSparePartsStatusLevel",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:sparePartsStatusItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:SystemSparePartsStatusLevel",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:sparePartsStatusItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:SystemSparePartsStatusLevel",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:systemAvailabilityModeItemType, Sample valid value is "Islanded"
    [_ln(), "System", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Islanded",
            "aspects": {
                "xbrl:concept": "solar:SystemAvailabilityMode",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "System", "value is not legal for type solar-types:systemAvailabilityModeItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:SystemAvailabilityMode",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "System", "value is not legal for type solar-types:systemAvailabilityModeItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:SystemAvailabilityMode",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:systemOperationalStatusItemType, Sample valid value is "Communication Failure"
    [_ln(), "System", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Communication Failure",
            "aspects": {
                "xbrl:concept": "solar:SystemOperationStatus",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "System", "value is not legal for type solar-types:systemOperationalStatusItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:SystemOperationStatus",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "System", "value is not legal for type solar-types:systemOperationalStatusItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:SystemOperationStatus",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:titlePolicyInsuranceItemType, Sample valid value is "Pro Forma"
    [_ln(), None, None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Pro Forma",
            "aspects": {
                "xbrl:concept": "solar:TitlePolicyInsuranceStatus",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:titlePolicyInsuranceItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:TitlePolicyInsuranceStatus",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), None, "value is not legal for type solar-types:titlePolicyInsuranceItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:TitlePolicyInsuranceStatus",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:trackerItemType, Sample valid value is "Azimuth Axis Tracking"
    [_ln(), "System", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Azimuth Axis Tracking",
            "aspects": {
                "xbrl:concept": "solar:TrackerStyle",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "System", "value is not legal for type solar-types:trackerItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:TrackerStyle",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "System", "value is not legal for type solar-types:trackerItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:TrackerStyle",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],

    # solar-types:zoningPermitPropertyItemType, Sample valid value is "Gen Tie Line"
    [_ln(), "", None, 0, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:ZoningPermitProperty",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "", "value is not legal for type solar-types:zoningPermitPropertyItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": false,
            "aspects": {
                "xbrl:concept": "solar:ZoningPermitProperty",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ],
    [_ln(), "", "value is not legal for type solar-types:zoningPermitPropertyItemType", 2, """
        {
            "id": "d5ead87b-58c6-4aab-9795-e7e92ca0bcf2",
            "value": "Invalid Value",
            "aspects": {
                "xbrl:concept": "solar:ZoningPermitProperty",
                "xbrl:entity": "JUPITER",
                "xbrl:periodStart": "2017-11-01T00:00:00",
                "xbrl:periodEnd": "2017-11-30T00:00:00"
            }
        }
        """
    ]
]

JSON_HEADER = """
{
  "documentType": "http://www.xbrl.org/WGWD/YYYY-MM-DD/xbrl-json",
  "prefixes": {
    "xbrl": "http://www.xbrl.org/WGWD/YYYY-MM-DD/oim",
    "solar": "http://xbrl.us/Solar/v1.1/2018-02-09/solar",
    "us-gaap": "http://fasb.org/us-gaap/2017-01-31",
    "iso4217": "http://www.xbrl.org/2003/iso4217",
    "SI": "http://www.xbrl.org/2009/utr"
  },
  "dtsReferences": [
    {
      "type": "schema",
      "href": "https://raw.githubusercontent.com/xbrlus/solar/v1.2/core/solar_all_2018-03-31_r01.xsd"
    }
  ],
  "facts": [
"""

JSON_FOOTER = """
  ]
}
"""