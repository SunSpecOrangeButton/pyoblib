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

""" Parses JSON/XML input and output data. """

import data_model
import taxonomy
import util

import enum
import json
import xml.etree.ElementTree as ElementTree
import sys

# The Following code is used internally by the XML parser - there is no known general usage
# reason to leverage.  The extremely short function name is for brevity in the XML parser.

_xml_ns = {"xbrldi:": "{http://xbrl.org/2006/xbrldi}",
      "link:": "{http://www.xbrl.org/2003/linkbase}",
      "solar:": "{http://xbrl.us/Solar/v1.2/2018-03-31/solar}",
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
        Returns the name of the correct entrypoint given a set of concepts from a document (JSON or XML).
        Currently assumes that a JSON/XML document contains one and only one entrypoint and raises
        an exception if this is not true.

        doc_concepts (list of strings): A list of all concepts in the input JSON/XML

        TODO: This is algorithm is fairly slow since it loops through all entry points which is time
        consuming for a small number of input concepts.  With this said there is not currently enough
        support functions in Taxonomy to accomodate other algorithms.  It may be better to move this
        into taxonomy_semantic and simultaneously improve the speed.
        """ 

        eps_found = set()
        for ep in self._taxonomy.semantic.entry_points():
            for concept in self._taxonomy.semantic.concepts_ep(ep):
                for dc in doc_concepts:
                    if dc == concept:
                        eps_found.add(ep)

        if len(eps_found) == 0:
            raise Exception("No entrypoint found given the set of facts")
        elif len(eps_found) == 1:
            for ep in eps_found:
                return ep
        else:
            # Multiple candidate entrypoints are found.  See if there is one and only one
            # perfect fit.
            the_one = None
            for ep in eps_found:
                ok = True
                for c in doc_concepts:
                    ok2 = False
                    for c2 in self._taxonomy.semantic.concepts_ep(ep):
                        if c == c2:
                            ok2 = True
                            break
                    if not ok2:
                        ok = False
                        break
                if ok:
                    if the_one is None:
                        the_one = ep
                    else:
                        raise Exception("Multiple entrypoints found given the set of facts")
            if the_one == None:
                raise Exception("No entrypoint found given the set of facts")
            else:
                return the_one

    def from_JSON_string(self, json_string):
        """ 
        Loads the Entrypoint from a JSON string into an entrypoint

        json_string (str): String containing JSON
        """

        # Convert string to JSON data
        json_data = json.loads(json_string)

        # Perform basic validation that all required parts of the document are present.
        if "documentType" not in json_data:
            raise Exception("JSON is missing documentType tag")
        if "prefixes" not in json_data:
            raise Exception("JSON is missing prefixes tag")
        if "dtsReferences" not in json_data:
            raise Exception("JSON is missing dtsRererences tag")
        if "facts" not in json_data:
            raise Exception("JSON is missing facts tag")

        # Loop through facts to determine what type of endpoint this is.
        facts = json_data["facts"]
        fact_names = []
        for fact in facts:
            fact_names.append(fact["aspects"]["xbrl:concept"])
    
        # Create an entrypoint.
        entrypoint = data_model.Entrypoint(self._entrypoint_name(fact_names), self._taxonomy, dev_validation_off=True)

        # Loop through facts.
        facts = json_data["facts"]
        for fact in facts:

            # Create kwargs and populate with entity.
            kwargs = {"entity": fact["aspects"]["xbrl:entity"]}

            # TODO: id is not currently support by Entrypoint.  Uncomment when it is.
            # if "id" in fact:
            #     kwargs["id"] = fact["id"]

            if "xbrl:periodStart" in fact["aspects"] and "xbrl:periodEnd" in fact["aspects"]:
                if fact["aspects"]["xbrl:periodStart"] == fact["aspects"]["xbrl:periodEnd"]:
                    kwargs["instant"] = util.convert_json_datetime(fact["aspects"]["xbrl:periodStart"])
                else:
                    kwargs["duration"] = {}
                    kwargs["duration"]["start"] = util.convert_json_datetime(fact["aspects"]["xbrl:periodStart"])
                    kwargs["duration"]["end"] = util.convert_json_datetime(fact["aspects"]["xbrl:periodEnd"])
            else:
                kwargs["duration"] = "forever"

            if "xbrl:unit" in fact["aspects"]:
                kwargs["unit_name"] = fact["aspects"]["xbrl:unit"]

            # Add axis to kwargs if item is an axis.
            for axis_chk in fact["aspects"]:
                if "Axis" in axis_chk:
                    kwargs[axis_chk.split(":")[1]] = fact["aspects"][axis_chk]

            entrypoint.set(fact["aspects"]["xbrl:concept"], fact["value"], **kwargs)

        return entrypoint

    def from_JSON(self, in_filename):
        """
        Imports XBRL as JSON from the given filename.
        
        in_filename(str): input filename
        """

        with open(in_filename, "r") as infile: 
            s = infile.read()
        return self.from_JSON_string(s)

    def from_XML_string(self, xml_string):
        """
        Loads the Entrypoint from an XML string

        xml_string(str): String containing XML.
        """

        root = ElementTree.fromstring(xml_string)
        # Read all elements that are not a context or a unit:
        fact_names = []
        for child in root:
            if child.tag != _xn("link:schemaRef") and child.tag != _xn("unit") and child.tag != _xn("context"):

                tag = child.tag
                tag = tag.replace("{http://xbrl.us/Solar/v1.2/2018-03-31/solar}", "solar:")
                tag = tag.replace("{http://fasb.org/us-gaap/2017-01-31}", "us-gaap:")
                tag = tag.replace("{http://xbrl.sec.gov/dei/2014-01-31}", "dei:")
                fact_names.append(tag)

        # Create an entrypoint.
        entrypoint = data_model.Entrypoint(self._entrypoint_name(fact_names), self._taxonomy)

        # TODO: Supply implementation upon completion of prototype code.
        print("WARNING: Implementation is not complete !!")
        print("Entrypoint detected:", self._entrypoint_name(fact_names))
        print("An empty Entrypoint is returned")
        print("Upon completion a populated Entrypoint will be returned.")
        
        return entrypoint

        """
        PROTOTYPE CODE:
        This will currently crash.  It can be added to from_XML_String once it is working.  Minor
        tweaking will be required to ensure correct operation.

        # Read in units
        units = {}
        for unit in root.iter(nn("unit")):
            units[unit.attrib["id"]] = unit[0].text

        # Read in contexts
        contexts = {}
        for context in root.iter(nn("context")):
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
                        start_date = elem[0].tag.text
                    elif elem[0].tag == _xn("endDate"):
                        end_date = elem[0].tag.text
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
                    # print(a)
                    kwargs[a] = axis[a]
            # print("=====")
            # print(axis)
            # print(kwargs)
            dm_ctx = data_model.Context(**kwargs)
            # print(dm_ctx)
            # print("=====")
            contexts[context.attrib["id"]] = dm_ctx

        # Read all elements that are not a context or a unit:
        for child in root:
            if child.tag != _xn("link:schemaRef") and child.tag != _xn("unit") and child.tag != _xn("context"):
                kwargs = {}
                if "contextRef" in child.attrib:
                    kwargs["context"] = contexts[child.attrib["contextRef"]]

                tag = child.tag
                tag = tag.replace("{http://xbrl.us/Solar/v1.2/2018-03-31/solar}", "solar:")
                tag = tag.replace("{http://fasb.org/us-gaap/2017-01-31}", "us-gaap:")
                tag = tag.replace("{http://xbrl.sec.gov/dei/2014-01-31}", "dei:")

                print("============")
                print("concept_name:", tag)
                print("value:", child.text)
                print("kwargs", kwargs)
                print("kwargs['context'].instant:", kwargs["context"].instant)
                print("kwargs['context'].duration:", kwargs["context"].duration)
                print("kwargs['context'].entity:", kwargs["context"].entity)
                print("kwargs['context'].axes:", kwargs["context"].axes)
                print("Calling doc.set(concept_name, value, **kwargs)")
                doc.set(tag, child.text, 

        """

    def from_XML(self, in_filename):
        """ 
        Imports XBRL as XML from the given filename.

        in_filename (str): input filename
        """

        with open(in_filename, "r") as infile: 
            s = infile.read()
        return self.from_XML_string(s)

    def to_JSON_string(self, entrypoint):
        """
        Returns XBRL as an JSON string given a data model entrypoint.

        entrypoint (Entrypoint): entry point to export to JSON
        """

        return entrypoint.to_JSON_string()

    def to_JSON(self, entrypoint, out_filename):
        """ 
        Exports XBRL as JSON to the given filename given a data model entrypoint. 

        entrypoint (Entrypoint): entry point to export to JSON
        out_filename (str): output filename
        """
        
        entrypoint.to_JSON(out_filename)

    def to_XML_string(self, entrypoint):
        """ 
        Returns XBRL as an XML string given a data model entrypoint.
        
        entrypoint (Entrypoint): entry point to export to XML
        """

        return entrypoint.to_XML_string()

    def to_XML(self, entrypoint, out_filename):
        """ 
        Exports XBRL as XML to the given filename given a data model entrypoint. 
        
        entrypoint (Entrypoint): entry point to export to XML
        out_filename (str): output filename
        """
        
        entrypoint.to_XML(out_filename)

    def convert(self, in_filename, out_filename, file_format):
        """ 
        Converts and input file (in_filename) to an output file (out_filename) given an input 
        file format specified by file_format.

        in_filename (str): full path to input file
        out_filename (str): full path to output file
        file_format (FileFormat): values are FileFormat.JSON" or FileForamt.XML"
        """

        if file_format == FileFormat.JSON:
            entrypoint = self.from_JSON(in_filename)
            self.to_XML(entrypoint, out_filename)
        elif file_format == FileFormat.XML:
            entrypoint = self.from_XML(in_filename)
            self.to_JSON(entrypoint, out_filename)
        else:
            raise ValueError("file_format must be JSON or XML")

    def validate(self, in_filename, file_format):
        """
        Validates an in input file (in_filename) by loading it.  Unlike convert does not produce
        an output file.

        in_filename (str): full path to input file
        file_format (FileFormat): values are FileFormat.JSON" or FileForamt.XML"

        TODO: At this point in time errors part output via print statements.  Future implementation
        should actually return the conditions instead.  It also may be desirable to list the 
        strictness level of the validation checkes.
        """

        if file_format == FileFormat.JSON:
            self.from_JSON(in_filename)
        else:
            self.from_XML(in_filename)
