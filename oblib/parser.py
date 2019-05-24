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

""" Parses JSON/XML input and output data. """


import enum
import json
import xml.etree.ElementTree as ElementTree
from oblib import data_model, util, ob


# The Following code is used internally by the XML parser - there is no known general usage
# reason to leverage.  The extremely short function name is for brevity in the XML parser.


_xml_ns = {"xbrldi:": "{http://xbrl.org/2006/xbrldi}",
      "link:": "{http://www.xbrl.org/2003/linkbase}",
      "solar:": "{http://xbrl.us/Solar/v1.3/2019-02-27/solar}",
      "dei:": "{http://xbrl.sec.gov/dei/2014-01-31}",
      "us-gaap:": "{http://fasb.org/us-gaap/2017-01-31}"}


def _xn(s):
    # eXpands the Namespace to be equitable to what is read in by the XML parser.

    if s is None:
        return None
    for n in _xml_ns:
        if n in s:
            return s.replace(n, _xml_ns[n])
    return "{http://www.xbrl.org/2003/instance}" + s 

# End of XML parsign utility code


class FileFormat(enum.Enum):
    """ Legal values for file formats. """

    XML = "XML"
    JSON = "JSON"


class Parser(object):
    """ 
    Parses JSON/XML input and output data 
    
    taxonomy (Taxonomy): initialized Taxonomy.
    """

    def __init__(self, taxonomy):
        """ Initializes parser """

        self._taxonomy = taxonomy

    def _entrypoint_name(self, doc_concepts):
        """ 
        Used to find the name of the correct entrypoint given a set of concepts from a document (JSON or XML).
        Currently assumes that a JSON/XML document contains one and only one entrypoint and raises
        an exception if this is not true.

        Args:
            doc_concepts (list of strings): A list of all concepts in the input JSON/XML document.

        Returns:
            A string contianing the name of the correct entrypoint.
        TODO: This is algorithm is fairly slow since it loops through all entry points which is time
        consuming for a small number of input concepts.  With this said there is not currently enough
        support functions in Taxonomy to accomodate other algorithms.  It may be better to move this
        into taxonomy_semantic and simultaneously improve the speed.
        """ 

        entrypoints_found = set()
        for entrypoint in self._taxonomy.semantic.get_all_entrypoints():
            if entrypoint == "All":
                # Ignore the "All" entrypoint, which matches everything -- we're
                # looking for a more specific one.
                continue
            for concept in self._taxonomy.semantic.get_entrypoint_concepts(entrypoint):
                for doc_concept in doc_concepts:
                    if doc_concept == concept:
                        entrypoints_found.add(entrypoint)

        if len(entrypoints_found) == 0:
            raise ob.OBValidationError("No entrypoint found given the set of facts")
        elif len(entrypoints_found) == 1:
            for entrypoint in entrypoints_found:
                return entrypoint
        else:
            # Multiple candidate entrypoints are found.  See if there is one and only one
            # perfect fit.
            the_one = None
            for entrypoint in entrypoints_found:
                ok = True
                for doc_concept in doc_concepts:
                    ok2 = False
                    for doc_concept2 in self._taxonomy.semantic.get_entrypoint_concepts(entrypoint):
                        if doc_concept == doc_concept2:
                            ok2 = True
                            break
                    if not ok2:
                        ok = False
                        break
                if ok:
                    if the_one is None:
                        the_one = entrypoint
                    else:
                         raise ob.OBValidationError("Multiple entrypoints ({}, {}) found given the set of facts".format(the_one, entrypoint))
            if the_one == None:
                raise ob.OBValidationError("No entrypoint found given the set of facts")
            else:
                return the_one

    def from_JSON_string(self, json_string, entrypoint_name=None):
        """ 
        Loads the Entrypoint from a JSON string into an entrypoint.  If no entrypoint_name
        is given the entrypoint will be derived from the facts.  In some cases this is not
        possible because more than one entrypoint could exist given the list of facts and
        in these cases an entrypoint is required.

        Args:
            json_string (str): String containing JSON
            entrypoint_name (str): Optional name of the entrypoint.

        Returns:
            OBInstance containing the loaded data.
        """

        # Create a validation error which can be used to maintain a list of error messages
        validation_errors = ob.OBValidationErrors("Error(s) found in input JSON")

        # Convert string to JSON data
        try:
            json_data = json.loads(json_string)
        except Exception as e:
            validation_errors.append(e)
            raise validation_errors

        # Perform basic validation that all required parts of the document are present.
        if "documentType" not in json_data:
            validation_errors.append("JSON is missing documentType tag")
            raise validation_errors
        if "prefixes" not in json_data:
            validation_errors.append("JSON is missing prefixes tag")
            raise validation_errors
        if "dtsReferences" not in json_data:
            validation_errors.append("JSON is missing dtsRererences tag")
            raise validation_errors
        if "facts" not in json_data:
            validation_errors.append("JSON is missing facts tag")
            raise validation_errors
        facts = json_data["facts"]

        # Loop through facts to determine what type of endpoint this is.
        if not entrypoint_name:
            fact_names = []
            for id in facts:
                fact = facts[id]
                if "aspects" not in fact:
                    validation_errors.append("fact tag is missing aspects tag")
                elif "concept" not in fact["aspects"]:
                    validation_errors.append("aspects tag is missing concept tag")
                else:
                    fact_names.append(fact["aspects"]["concept"])
            try:
                entrypoint_name = self._entrypoint_name(fact_names)
            except ob.OBValidationError as ve:
                validation_errors.append(ve)
                raise validation_errors

        # If we reach this point re-initialize the validation errors because all previous errors found
        # will be found again.  Re-initialization reduces duplicate error messages and ensures that
        # errors are found in the correct order.
        validation_errors = ob.OBValidationErrors("Error(s) found in input JSON")

        # Create an entrypoint.
        ob_instance = data_model.OBInstance(entrypoint_name, self._taxonomy, dev_validation_off=False)

        # Loop through facts.
        for id in facts:

            fact = facts[id]

            # Track the current number of errors to see if it grows for this fact
            begin_error_count = len(validation_errors.get_errors())

            # Create kwargs and populate with entity.
            kwargs = {}
            if "aspects" not in fact:
                validation_errors.append("fact tag is missing aspects tag")
            else:
                if "concept" not in fact["aspects"]:
                    validation_errors.append("aspects tag is missing concept tag")

                if "entity" not in fact["aspects"]:
                    validation_errors.append("aspects tag is missing entity tag")
                else:
                    kwargs = {"entity": fact["aspects"]["entity"]}

                # TODO: id is not currently support by Entrypoint.  Uncomment when it is.
                # if "id" in fact:
                #     kwargs["id"] = fact["id"]

                if "period" in fact["aspects"]:
                    period = fact["aspects"]["period"]
                    if "/" in period:
                        dates = period.split("/")
                        if len(dates) != 2:
                            validation_errors.append("period component is in an incorrect format (yyyy-mm-ddT00:00:00/yyyy-mm-ddT00:00:00 expected)")
                        else:
                            start = util.convert_json_datetime(dates[0])
                            end = util.convert_json_datetime(dates[1])
                            if start is None:
                                validation_errors.append("period start component is in an incorrect format (yyyy-mm-ddT00:00:00 expected)")
                            if end is None:
                                validation_errors.append("period end component is in an incorrect format (yyyy-mm-ddT00:00:00 expected)")
                            kwargs["duration"] = {}
                            kwargs["duration"]["start"] = start
                            kwargs["duration"]["end"] = end
                    else:
                        start = util.convert_json_datetime(fact["aspects"]["period"])
                        if start is None:
                            validation_errors.append("start is in an incorrect format (yyyy-mm-ddT00:00:00 expected)")
                        kwargs["instant"] = start

                elif kwargs is not None:
                    kwargs["duration"] = "forever"

                # Add axis to kwargs if item is an axis.
                # TODO: Exception processing
                for axis_chk in fact["aspects"]:
                    if "Axis" in axis_chk:
                        kwargs[axis_chk.split(":")[1]] = fact["aspects"][axis_chk]

            if "aspects" in fact and "unit" in fact["aspects"] and kwargs is not None:
                kwargs["unit_name"] = fact["aspects"]["unit"]

            if "value" not in fact:
                validation_errors.append("fact tag is missing value tag")

            kwargs["fact_id"] = id

            # If validation errors were found for this fact continute to the next fact
            if len(validation_errors.get_errors()) > begin_error_count:
                continue

            # TODO: Temporary code
            # Required to match behavior of to_JSON, once the two are synchronized it should not be required.
            value = fact["value"]
            if value == "None":
                value = None
            elif value == "True":
                value = True
            elif value == "False":
                value = False
            # Done with temporary code

            try:
                ob_instance.set(fact["aspects"]["concept"], value, **kwargs)
                # entrypoint.set(fact["aspects"]["xbrl:concept"], fact["value"], **kwargs)
            except Exception as e:
                validation_errors.append(e)

        # Raise the errors if necessary
        if validation_errors.get_errors():
            raise validation_errors

        return ob_instance

    def from_JSON(self, in_filename, entrypoint_name=None):
        """
        Imports XBRL as JSON from the given filename.    If no entrypoint_name
        is given the entrypoint will be derived from the facts.  In some cases this is not
        possible because more than one entrypoint could exist given the list of facts and
        in these cases an entrypoint is required.

        Args:
            in_filename (str): input filename
            entrypoint_name (str): Optional name of the entrypoint.

        Returns:
            OBInstance containing the loaded data.
        """

        with open(in_filename, "r") as infile: 
            s = infile.read()
        return self.from_JSON_string(s, entrypoint_name)

    def from_XML_string(self, xml_string, entrypoint_name=None):
        """
        Loads the Entrypoint from an XML string.    If no entrypoint_name
        is given the entrypoint will be derived from the facts.  In some cases this is not
        possible because more than one entrypoint could exist given the list of facts and
        in these cases an entrypoint is required.

        Args:
            xml_string(str): String containing XML.
            entrypoint_name (str): Optional name of the entrypoint.

        Returns:
            OBInstance containing the loaded data.
        """

        # NOTE: The XML parser has much less effort placed into both the coding and testing as
        # opposed to the coding and testing effort performed on the JSON parser.  To some extent
        # this is on purpose since the hope is that the bulk of Orange Button data will be
        # transmitted using JSON.  With this you are invited to (a) refactor the XML parsing code
        # and (b) create XML test cases if you believe that XML parser should receive the same 
        # effort level as the JSON parser.
  
        # Create a validation error which can be used to maintain a list of error messages
        validation_errors = ob.OBValidationErrors("Error(s) found in input JSON")

        try:
            root = ElementTree.fromstring(xml_string)
        except Exception as e:
            validation_errors.append(e)
            raise validation_errors

        # Read all elements that are not a context or a unit:
        if not entrypoint_name:
            fact_names = []
            for child in root:
                if child.tag != _xn("link:schemaRef") and child.tag != _xn("unit") and child.tag != _xn("context"):

                    tag = child.tag
                    tag = tag.replace("{http://xbrl.us/Solar/v1.3/2019-02-27/solar}", "solar:")
                    tag = tag.replace("{http://fasb.org/us-gaap/2017-01-31}", "us-gaap:")
                    tag = tag.replace("{http://xbrl.sec.gov/dei/2014-01-31}", "dei:")
                    fact_names.append(tag)
            try:
                entrypoint_name = self._entrypoint_name(fact_names)
            except ob.OBValidationError as ve:
                validation_errors.append(ve)
                raise validation_errors

        # Create an entrypoint.
        entrypoint = data_model.OBInstance(entrypoint_name, self._taxonomy, dev_validation_off=True)

        # Read in units
        units = {}
        for unit in root.iter(_xn("unit")):
            units[unit.attrib["id"]] = unit[0].text

        # Read in contexts
        contexts = {}
        for context in root.iter(_xn("context")):
            instant = None
            duration = None
            entity = None
            start_date = None
            end_date = None
            axis = {}
            for elem in context.iter():
                if elem.tag == _xn("period"):
                    if elem[0].tag == _xn("forever"):
                        duration = "forever"
                    elif elem[0].tag == _xn("startDate"):
                        start_date = elem[0].text
                    elif elem[0].tag == _xn("endDate"):
                        end_date = elem[0].text
                    elif elem[0].tag == _xn("instant"):
                        instant = elem[0].text
                elif elem.tag == _xn("entity"):
                    for elem2 in elem.iter():
                        if elem2.tag == _xn("identifier"):
                            entity = elem2.text
                        elif elem2.tag == _xn("segment"):
                            for elem3 in elem2.iter():
                                if elem3.tag == _xn("xbrldi:typedMember"):
                                    for elem4 in elem3.iter():
                                        if elem4.tag != _xn("xbrldi:typedMember"):
                                            axis[elem3.attrib["dimension"]] = elem4.text

            if duration is None and start_date is not None and end_date is not None:
                duration = {"start": start_date, "end": end_date}
            kwargs = {}
            if instant is not None:
                kwargs["instant"] = instant
            if duration is not None:
                kwargs["duration"] = duration
            if entity is not None:
                kwargs["entity"] = entity
            if axis is not None:
                for a in axis:
                    kwargs[a] = axis[a]

            if instant is None  and duration is None:
                validation_errors.append(
                    ob.OBValidationError("Context is missing both a duration and instant tag"))
            if entity is None:
                validation_errors.append("Context is missing an entity tag")

            try:
                dm_ctx = data_model.Context(**kwargs)
                contexts[context.attrib["id"]] = dm_ctx
            except Exception as e:
                validation_errors.append(e)

        # Read all elements that are not a context or a unit:
        for child in root:
            if child.tag != _xn("link:schemaRef") and child.tag != _xn("unit") and child.tag != _xn("context"):
                kwargs = {}

                fact_id = None
                if "id" in child.attrib:
                    fact_id = child.attrib["id"]

                if "contextRef" in child.attrib:
                    if child.attrib["contextRef"] in contexts:
                        kwargs["context"] = contexts[child.attrib["contextRef"]]
                        kwargs["fact_id"] = fact_id
                        tag = child.tag
                        tag = tag.replace("{http://xbrl.us/Solar/v1.3/2019-02-27/solar}", "solar:")
                        tag = tag.replace("{http://fasb.org/us-gaap/2017-01-31}", "us-gaap:")
                        tag = tag.replace("{http://xbrl.sec.gov/dei/2014-01-31}", "dei:")
                        try:
                            entrypoint.set(tag, child.text, **kwargs)
                        except Exception as e:
                            validation_errors.append(e)
                    else:
                        validation_errors.append("referenced context is missing")
                else:
                    validation_errors.append("Element is missing a context")

        # Raise the errors if necessary
        if validation_errors.get_errors():
            raise validation_errors

        # Return populated entrypoint
        return entrypoint

    def from_XML(self, in_filename, entrypoint_name=None):
        """ 
        Imports XBRL as XML from the given filename.  If no entrypoint_name
        is given the entrypoint will be derived from the facts.  In some cases this is not
        possible because more than one entrypoint could exist given the list of facts and
        in these cases an entrypoint is required.

        Args:
            in_filename (str): input filename
            entrypoint_name (str): Optional name of the entrypoint.

        Returns:
            OBInstance containing the loaded data.
        """

        with open(in_filename, "r") as infile: 
            s = infile.read()
        return self.from_XML_string(s, entrypoint_name)

    def to_JSON_string(self, entrypoint):
        """
        Returns XBRL as an JSON string given a data model entrypoint.

        entrypoint (Entrypoint): entry point to export to JSON
        """

        return entrypoint.to_JSON_string()

    def to_JSON(self, entrypoint, out_filename):
        """ 
        Exports XBRL as JSON to the given filename given a data model entrypoint. 

        Args:
            entrypoint (Entrypoint): entry point to export to JSON
            out_filename (str): output filename
        """
        
        entrypoint.to_JSON(out_filename)

    def to_XML_string(self, entrypoint):
        """ 
        Returns XBRL as an XML string given a data model entrypoint.

        Args:
            entrypoint (Entrypoint): entry point to export to XML
        """

        return entrypoint.to_XML_string()

    def to_XML(self, entrypoint, out_filename):
        """ 
        Exports XBRL as XML to the given filename given a data model entrypoint. 

        Args:
            entrypoint (Entrypoint): entry point to export to XML
            out_filename (str): output filename
        """
        
        entrypoint.to_XML(out_filename)

    def convert(self, in_filename, out_filename, file_format, entrypoint_name=None):
        """ 
        Converts and input file (in_filename) to an output file (out_filename) given an input 
        file format specified by file_format.  If no entrypoint_name
        is given the entrypoint will be derived from the facts.  In some cases this is not
        possible because more than one entrypoint could exist given the list of facts and
        in these cases an entrypoint is required.

        Args:
            in_filename (str): full path to input file
            out_filename (str): full path to output file
            entrypoint_name (str): Optional name of the entrypoint.
            file_format (FileFormat): values are FileFormat.JSON" or FileFormat.XML"
        """

        if file_format == FileFormat.JSON:
            entrypoint = self.from_JSON(in_filename, entrypoint_name)
            self.to_XML(entrypoint, out_filename)
        elif file_format == FileFormat.XML:
            entrypoint = self.from_XML(in_filename, entrypoint_name)
            self.to_JSON(entrypoint, out_filename)
        else:
            raise ValueError("file_format must be JSON or XML")

    def validate(self, in_filename, file_format, entrypoint_name=None):
        """
        Validates an in input file (in_filename) by loading it.  Unlike convert does not produce
        an output file.  If no entrypoint_name
        is given the entrypoint will be derived from the facts.  In some cases this is not
        possible because more than one entrypoint could exist given the list of facts and
        in these cases an entrypoint is required.

        Args:
            in_filename (str): full path to input file
            entrypoint_name (str): Optional name of the entrypoint.
            file_format (FileFormat): values are FileFormat.JSON" or FileFormat.XML"

        TODO: At this point in time errors part output via print statements.  Future implementation
        should actually return the conditions instead.  It also may be desirable to list the 
        strictness level of the validation checkes.
        """

        if file_format == FileFormat.JSON:
            self.from_JSON(in_filename, entrypoint_name)
        else:
            self.from_XML(in_filename, entrypoint_name)
