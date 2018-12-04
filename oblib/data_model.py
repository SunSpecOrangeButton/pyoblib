# Copyright 2018 Jonathan Xia

# Licensed under the Apache License, Version 2.0 (the "License");
# pyou may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import xml.etree.ElementTree
from xml.etree.ElementTree import Element, SubElement
import datetime
import json

class Hypercube(object):
    """
    (Currently a placeholder) a data structure to represent a table
    (aka a Hypercube) within a document.
    """
    def __init__(self, table_name, axis_names):
        self._table_name = table_name
        self._axis_names = axis_names
        self._allowed_line_items = []
        # self.contexts stores a list of contexts that have been populated within
        # this table instance.
        self.contexts = []

    def name(self):
        return self._table_name

    def axes(self):
        return self._axis_names

    def addLineItem(self, line_item_name):
        """
        line_item_name is a string naming a concept. Call this function to tell
        the hypercube that the named concept is an allowable line item within
        this table.
        """
        self._allowed_line_items.append(line_item_name)

    def hasLineItem(self, line_item_name):
        return line_item_name in self._allowed_line_items

    def store_context(self, new_context):
        """
        Either creates and stores a new context or returns an already
        existing one matching kwargs.
        """

        # If we already have an equal context, re-use that one instead of creating
        # another. Otherwise, assign the new context an ID within this table.
        for context in self.contexts:
            if context.equals_context(new_context):
                return context
        # For the ID, just use "HypercubeName_serialNumber":
        new_id = "%s_%d" % (self._table_name, len(self.contexts))
        new_context.set_id(self, new_id)
        self.contexts.append(new_context)
        return new_context

    def lookup_context(self, old_context):
        for context in self.contexts:
            if context.equals_context(old_context):
                return context
        return None

    def toXML(self):
        return [context.toXML() for context in self.contexts]

    def isTypedDimension(self, dimensionName):
        # return (dimensionName in self.typedDimensionDomains)
        return False

    def getDomain(self, dimensionName):
        # this should be: self.ts.concept_info('solar:ProductIdentifierAxis').typed_domain_ref
        # return self.typedDimensionDomains[dimensionName]
        return ""


class Context(object):
    """
    """
    def __init__(self, **kwargs):
        self.instant = None
        self.duration = None
        self.entity = None
        # kwargs must provide exactly one of instant or duration
        if "instant" in kwargs and "duration" in kwargs:
            raise Exception("Context given both instant and duration")
        if (not "instant" in kwargs) and (not "duration" in kwargs):
            raise Exception("Context not given either instant or duration")
        if "instant" in kwargs:
            self.instant = kwargs.pop("instant")
        if "duration" in kwargs:
            self.duration = kwargs.pop("duration")
        if "entity" in kwargs:
            self.entity = kwargs.pop("entity")
        # anything that's not instant/duration or entity must be an axis
        self.axes = {}
        for keyword in kwargs:
            if not keyword.endswith("Axis"):
                # TODO in the future we should use metadata to identify
                # what's an axis, not just look for the string "Axis".
                raise Exception("Context given invalid keyword {}".format(keyword))
            qualified_name = "solar:" + keyword
            self.axes[qualified_name] = kwargs[keyword]

        # TODO store a reference to my parent hypercube?
        self.id_scheme = "http://xbrl.org/entity/identification/scheme" #???

    def set_cube(self, hypercube):
        self.hypercube = hypercube

    def equals_context(self, other_context):
        if other_context.entity != self.entity:
            return False

        if other_context.instant != self.instant:
            return False

        if other_context.duration != self.duration:
            # TODO does this work if they're tuples of (start, end) ?
            return False

        for axis_name, axis_value in self.axes.items():
            if not axis_name in other_context.axes:
                return False
            if axis_value != other_context.axes[axis_name]:
                return False

        for axis_name in other_context.axes:
            if not axis_name in self.axes:
                # extra axes in other context not present in this one:
                return False

        return True

    def set_id(self, hypercube, new_id):
        self.hypercube = hypercube
        self._id = new_id

    def get_id(self):
        return self._id

    def toXML(self):
        # if neither prod_month nor instant is provided, then period will
        # be "forever"
        context = Element("context", attrib={"id": self.get_id()})
        entity = SubElement(context, "entity")
        identifier = SubElement(entity, "identifier",
                                attrib={"scheme": self.id_scheme})
        identifier.text = self.entity

        # Period (instant or duration):
        period = SubElement(context, "period")

        if self.duration == "forever":
            forever = SubElement(period, "forever")
        elif self.duration is not None:
            startDate = SubElement(period, "startDate")
            startDate.text = self.duration[0].strftime("%Y-%m-%d")
            endDate = SubElement(period, "endDate")
            endDate.text = self.duration[1].strftime("%Y-%m-%d")
        elif self.instant is not None:
            instant_elem = SubElement(period, "instant")
            instant_elem.text = self.instant.strftime("%Y-%m-%d")


        # Extra dimensions:
        if len(self.axes) > 0:
            segmentElem = SubElement(entity, "segment")

        for dimension in self.axes:
            # First figure out if dimension is typed or untyped:

            if self.hypercube.isTypedDimension(dimension):
                typedMember = SubElement(
                    segmentElem, "xbrldi:typedMember",
                    attrib = {"dimension": dimension})
                domainElem = self.hypercube.getDomain(dimension)
                domain = SubElement(typedMember, domainElem)
                domain.text = str(self.axes[dimension])

            else:
                # if it's not one of the above, then it's an explicit dimension:
                explicit = SubElement(segmentElem, "xbrldi:explicitMember", attrib={
                    "dimension": dimension
                    })
                explicit.text = str(self.axes[dimension])
        return context

    def toJSON(self):
        """
        Returns context's entity, period, and extra dimensions as JSON dictionary
        object.
        """
        aspects = {"xbrl:entity": self.entity}
        if self.duration == "forever":
            aspects["xbrl:period"] = "forever" # TODO is this right syntax???
        elif self.duration is not None:
            aspects["xbrl:periodStart"] = self.duration[0].strftime("%Y-%m-%d")
            aspects["xbrl:periodEnd"] = self.duration[1].strftime("%Y-%m-%d")
        elif self.instant is not None:
            aspects["xbrl:instant"] = self.instant.strftime("%Y-%m-%d")
            # TODO is this the right syntax???

        for dimension in self.axes:
            # TODO is there a difference in how typed axes vs explicit axes
            # are represented in JSON?
            if self.hypercube.isTypedDimension(dimension):
            #if dimension in self.typedDimensionDomains:
                value_str = self.axes[dimension]
            else:
                value_str = self.axes[dimension]
            aspects[dimension] = value_str

        return aspects


class Fact(object):
    """
    Represents an XBRL Fact, linked to a context, that can be exported
    as either XML or JSON.
    """
    def __init__(self, concept, context, units, value, decimals=2):
        """
        Concept is the field name - it must match the schema definition.
        Context is a reference to this fact's parent Context object.
        Units is a string naming the unit, for example "kWh"
        Value is a string, integer, or float
        Decimals is used only for float types, it is the number of
        digits 
        """
        # in case of xml the context ID will be rendered in the fact tag.
        # in case of json the contexts' attributes will be copied to the
        # fact's aspects.
        self.concept = concept
        self.value = value
        self.context = context
        self.units = units
        self.decimals = decimals

    def toXML(self):
        """
        Return the Fact as an XML element.
        """
        attribs = {"contextRef": self.context.get_id()}
        if self.units is not None:
            attribs["unitRef"] = self.units
            if self.units == "pure" or self.units == "degrees":
                attribs["decimals"] = "0"
            else:
                attribs["decimals"] = str(self.decimals)
        elem = Element(self.concept, attrib=attribs)
        if self.units == "pure":
            elem.text = "%d" % self.value
        else:
            elem.text = str(self.value)
        return elem


    def toJSON(self):
        """
        Return the Fact as a JSON dictionary object
        """
        aspects = self.context.toJSON()
        aspects["xbrl:concept"] = self.concept
        if self.units is not None:
            aspects["xbrl:unit"] = self.units

        if isinstance( self.value, datetime.datetime):
            value_str = self.value.strftime("%Y-%m-%d")
        else:
            value_str = str(self.value)
        return { "aspects": aspects,
                 "value": value_str}


class Concept(object):
    """
    Currently only used as nodes in a tree data structure to keep track of which
    concepts are parents/children of other concepts in the schema hierarchy.
    """
    def __init__(self, concept_name):
        self.name = concept_name
        self.parent = None
        self.children = []

        # Some info we might want this class to store about its concept:
        # concept_ancestors = EntryPoint.all_my_concepts[concept].getAncestors()
        # concept_metadata = EntryPoint.ts.concept_info(concept)

        # concept_metadata properties:
        #x.period_type
        #x.nillable
        #x.id
        #x.name
        #x.substitution_group
        #x.type_name
        #x.period_independent
        # Which will be useful for validation.


    def setParent(self, new_parent):
        self.parent = new_parent
        if not self in self.parent.children:
            self.parent.children.append(self)

    def addChild(self, new_child):
        if not new_child in self.children:
            self.children.append(new_child)
        new_child.parent = self

    def getAncestors(self):
        # returns a list of concept's parent, concept's parent's parent, etc.
        ancestors = []
        curr = self
        while curr.parent is not None:
            ancestors.append(curr.parent)
            curr = curr.parent
        return ancestors


class Entrypoint(object):
    """
    A data structure representing an orange button document
    from a particular entrypoint -- for example, an MOR.
    This class's representation of the data is format-agnostic, it just
    provides methods for getting/setting and validation; translation to
    and from particular physical file format (or database schema) will
    be handled elsewhere.
    """
    def __init__(self, entrypoint_name, taxonomy):
        """
        Initializes an empty instance of a document corresponding to the named
        entrypoint. entrypoint_name is a string that must match an entry point in
        the taxonomy. Looks up the list of concepts for this entry point from
        the taxonomy to know what concepts are allowed in the document.
        Looks up the relationships between concepts for this entry point from
        the taxonomy to know the hierarchical relationship of concepts, tables,
        and axes/dimensions.
        taxonomy_semantic should be the global singleton TaxonomySemantic
        object.
        """
        self.ts = taxonomy.semantic
        self.entrypoint_name = entrypoint_name
        if not self.ts.validate_ep(entrypoint_name):
            raise Exception("There is no Orange Button entrypoint named {}."\
                                .format(entrypoint_name))

        # This gives me the list of every concept that could ever be
        # included in the document.

        self._all_allowed_concepts = self.ts.concepts_ep(entrypoint_name)

        # ts.concepts_info_ep(entrypoint_name)  # fails on
        # u'solar:MeterRatingAccuracy:1'

        # Get the relationships (this comes from solar_taxonomy/documents/
        #  <entrypoint>/<entrypoint><version>_def.xml)
        self.relations = self.ts.relationships_ep(entrypoint_name)
        # Search through the relationships to find all of the tables, their
        # axes, and parent/child relationships between concepts:
        self._find_tables()
        self._find_parents()

        self.facts = {}
        self.namespaces = {
            "xmlns": "http://www.xbrl.org/2003/instance",
            "xmlns:link": "http://www.xbrl.org/2003/linkbase",
            "xmlns:xlink": "http://www.w3.org/1999/xlink",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xmlns:units": "http://www.xbrl.org/2009/utr",
            "xmlns:xbrldi": "http://xbrl.org/2006/xbrldi",
            "xmlns:solar": "http://xbrl.us/Solar/v1.2/2018-03-31/solar"
        }
        self.taxonomy = "https://raw.githubusercontent.com/xbrlus/solar/v1.2/core/solar_2018-03-31_r01.xsd"



    def allowedConcepts(self):
        return self._all_allowed_concepts

    def _find_tables(self):
        """
        Uses relations to find all of the tables (hypercubes) allowed in
        the document, and the axes and lineitems for each one.
        """
        # When there's an arcrole of "hypercube-dimensions", the "from"
        # is a hypercube/table, and the "to" is an axis.
        self._tables = {}
        axes = {}
        # TODO move more of this logic to Hypercube constructor.
        for relation in self.relations:
            if relation['role'] == 'hypercube-dimension':
                table_name = relation['from']
                axis_name = relation['to']
                if not table_name in axes:
                    axes[table_name] = []
                axes[table_name].append(axis_name)
        for table_name in axes:
            # TODO let's initialize a Concept instance for each axis,
            # pass those instances to the Hypercube instead of just
            # their names.
            self._tables[table_name] = Hypercube( table_name, axes[table_name] )

        # If there's an arcrole of "all" then the "from" is a LineItems
        # and the "to" is the table?  I think?
        for relation in self.relations:
            if relation['role'] == 'all':
                line_item = relation['from']
                table_name = relation['to']
                table = self._tables[table_name]
                table.addLineItem(line_item)


    def _find_parents(self):
        # Put the concepts into a tree based on domain-member
        # relations.
        all_my_concepts = {}
        for relation in self.relations:
            if relation['role'] == 'domain-member':
                parent = relation['from']
                child = relation['to']
                if not parent in all_my_concepts:
                    all_my_concepts[parent] = Concept(parent)
                if not child in all_my_concepts:
                    all_my_concepts[child] = Concept(child)
                all_my_concepts[parent].addChild(all_my_concepts[child])
        self.all_my_concepts = all_my_concepts

    def getTableNames(self):
        return self._tables.keys()

    def getTable(self, table_name):
        return self._tables[table_name]

    def _identify_relations(self, concept_name):
        # Development method for listing all relationships for debugging
        # purposes. Do not use in production.
        from_me = [r for r in self.relations if r['from'] == concept_name]
        for x in from_me:
            print( "{} -> {} -> {}".format(concept_name, x['role'], x['to']))
        to_me = [r for r in self.relations if r['to'] == concept_name]
        for x in to_me:
            print( "{} -> {} -> {}".format(x['from'], x['role'], concept_name))

    def getTableForConcept(self, concept_name):
        """
        Given a concept_name, returns the table (Hypercube object) which
        that concept belongs inside of, or None if there's no match.
        """
        if not concept_name in self._all_allowed_concepts:
            raise Exception("{} is not an allowed concept for {}".format(
                concept_name, self.entrypoint_name))

        # We know that a concept belongs in a table because the concept
        # is a descendant of a LineItem that has a relationship to the
        # table.
        if not concept_name in self.all_my_concepts:
            return None
        ancestors = self.all_my_concepts[concept_name].getAncestors()
        for ancestor in ancestors:
            if "LineItem" in ancestor.name:
                for table in self._tables.values():
                    if table.hasLineItem(ancestor.name):
                        return table
        return None

    def canWriteConcept(self, concept_name):
        """
        Returns True if concept_name is a writeable concept within this
        document. False for concepts not in this document or concepts that
        are only abstract parents of writeable concepts. e.g. you can't
        write a value to an "Abstract" or a "LineItem".
        """
        if concept_name in self.all_my_concepts:
            abstract_keywords = ["Abstract", "LineItems", "Table", "Domain", "Axis"]
            for word in abstract_keywords:
                if concept_name.endswith(word):
                    return False
            return True
        return False

    def sufficientContext(self, concept_name, context):
        """
        True if the given Context object contains all the information
        needed to provide full context for the named concept -- sufficient
        time period information (duration/instant), sufficient axes to place
        the fact within its table, etc.
        Otherwise, raises an exception explaining what is wrong.
        """
        # TODO Refactor to put this logic into the Concept?
        metadata = self.ts.concept_info(concept_name)
        if metadata.period_type == "duration":
            if not context.duration:
                raise Exception("Missing required duration in {} context".format(
                    concept_name))

            # a valid duration is either "forever" or {"start", "end"}
            valid = False
            if context.duration == "forever":
                valid = True
            if "start" in context.duration and "end" in context.duration:
                # TODO check isinstance(duration["start"], datetime)
                valid = True
            if not valid:
                raise Exception("Invalid duration in {} context".format(
                    concept_name))


        if metadata.period_type == "instant":
            if not context.instant:
                raise Exception("Missing required instant in {} context".format(
                    concept_name))
                # TODO check isinstance(instant, datetime)

        # If we got this far, we know the time period is OK. Now check the
        # required axes, if this concept is on a table:
        table = self.getTableForConcept(concept_name)
        if table is not None:
            for axis in table.axes():
                if not axis in context.axes:
                    raise Exception("Missing required {} axis for {}".format(
                        axis, concept_name))
                # Check that the value given of context.axes[axis] is valid!
                # (How do we do that?)
        # TODO check that we haven't given any EXTRA axes that the table
        # DOESN'T want?

        return True


    def set(self, concept, value, **kwargs):
        """
        (Placeholder) Adds a fact to the document. The concept and the context
        together identify the fact to set, and the value will be stored for
        that fact.
        If concept and context are identical to a previous call, the old fact
        will be overwritten. Otherwise, a new fact is created.
        acceptable keyword args:
        unit = <unit name>
        precision = <number of places past the decimal pt>(for decimal values only)
        context = a Context object

        can be supplied as separate keyword args instead of context object:
        duration = "forever" or {"start": <date>, "end": <date>}
        instant = <date>
        entity = <entity name>
        *Axis = <value>  (the name of any Axis in a table in this entrypoint)
        """

        if "unit" in kwargs:
            unit = kwargs.pop("unit")
        else:
            unit = "None"
        if "precision" in kwargs:
            precision = kwargs.pop("precision")

        if not concept in self._all_allowed_concepts:
            raise Exception("{} is not allowed in the {} entrypoint".format(
                concept, self.entrypoint_name))
        if not self.canWriteConcept(concept):
            raise Exception("{} is not a writeable concept".format(concept))

        if "context" in kwargs:
            context = kwargs.pop("context")
        elif len(kwargs.keys()) > 0:
            # turn the remaining keyword args into a Context object -- this
            # is just syntactic sugar to make this method easier to call.
            context = Context(**kwargs)
        else:
            context = None
            # TODO:
            # In this case, use the default context if one has been set.

        if not self.sufficientContext(concept, context):
            raise Exception("Insufficient context given for {}".format(concept))

        table = self.getTableForConcept(concept)

        # complain if value is invalid for concept
        # complain if context is needed and not present
        # complain if context has wrong unit
        # complain if context has wrong duration/instant type
        # add to facts

        context = table.store_context(context) # dedupes, assigns ID

        f = Fact(concept, context, unit, value)
        # TODO pass in decimals? Fact expects decimals and "precision" is slightly different

        # self.facts is nested dict keyed first on table then on context ID
        # and finally on concept:
        if not table.name() in self.facts:
            self.facts[table.name()] = {}
        if not context.get_id() in self.facts[table.name()]:
            self.facts[table.name()][context.get_id()] = {}
        # TODO simplify above with defaultdict
        
        self.facts[table.name()][context.get_id()][concept] = f
        # Or: we could keep facts in a flat list, and get() could look them
        # up by getting context from hypercube and getting fact from context



    def get(self, concept, context=None):
        """
        Returns the value of a fact previously set. The concept
        and context together identify the fact to read.
        """
        # look up the facts we have
        # complain if no value for concept
        # complain if context needed and not providedd

        # TODO support case where no context passed in?  (use default
        # context I guess?)

        # TODO support getting by kwargs instead of getting by context?

        table = self.getTableForConcept(concept)
        context = table.lookup_context(context)
        if table.name() in self.facts:
            if context.get_id() in self.facts[table.name()]:
                if concept in self.facts[table.name()][context.get_id()]:
                    return self.facts[table.name()][context.get_id()][concept]
        return None

    def get_facts(self):
        # return flattened list of facts
        all_facts = []
        for table_dict in self.facts.values():
            for context_dict in table_dict.values():
                for fact in context_dict.values():
                    all_facts.append(fact)
        return all_facts


    def toXMLTag(self):
        # The root element:
        xbrl = Element("xbrl", attrib = self.namespaces)

        # Add "link:schemaRef" for the taxonomy that goes with this document:
        link = SubElement(xbrl, "link:schemaRef",
                          attrib = {"xlink:href": self.taxonomy,
                                    "xlink:type": "simple"})

        # Add a context tag for each context we want to reference:
        for hypercube in self._tables.values():
            tags = hypercube.toXML()
            for tag in tags:
                xbrl.append(tag)

        # TODO support units:
        #for unit in self.get_required_units():
        #    # Add a unit tag defining each unit we want to reference:
        #    xbrl.append(self.makeUnitTag(unit))

        for fact in self.get_facts():
            xbrl.append( fact.toXML() )

        return xbrl

    def toXML(self, filename):
        """
        Exports XBRL as XML to the given filename.
        """
        xbrl = self.toXMLTag()
        tree = xml.etree.ElementTree.ElementTree(xbrl)
        # Apparently every XML file should start with this, which ElementTree
        # doesn't do:
        # <?xml version="1.0" encoding="utf-8"?>
        tree.write(filename)

    def toXMLString(self):
        """
        Returns XBRL as an XML string
        """
        xbrl = self.toXMLTag()
        return xml.etree.ElementTree.tostring(xbrl).decode()


    def toJSON(self, filename):
        """
        Exports XBRL as JSON to the given filename.
        """

        outfile = open(filename, "w")
        outfile.write(self.toJSONString())
        outfile.close()

    def toJSONString(self):
        """
        Returns XBRL as a JSON string
        """
        masterJsonObj = {
            "documentType": "http://www.xbrl.org/WGWD/YYYY-MM-DD/xbrl-json",
            "prefixes": self.namespaces,
            "dtsReferences": [],
            "facts": []
            }

        masterJsonObj["dtsReferences"].append({
            "type": "schema",
            "href": self.taxonomy
        })

        facts = self.get_facts()

        for fact in facts:
            masterJsonObj["facts"].append( fact.toJSON() )
        return json.dumps(masterJsonObj)


    def isValid(self):
        """
        (Placeholder) Returns true if all of the facts in the document validate.
        i.e. they have allowed data types, allowed units, anything that needs
        to be in a table has all the required axis values to identify its place
        in that table, etc.
        """
        return True

    def isComplete(self):
        """
        (Placeholder) Returns true if no required facts are missing, i.e. if
        there is a value for all concepts with nillable=False
        """
        return True

