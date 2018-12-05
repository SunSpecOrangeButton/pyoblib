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


class Axis(object):
    """
    A table axis. A concept with some extra stuff.
    """
    def __init__(self, concept):
        self.concept = concept
        self.domain = None
        self.domainMembers = []


class Hypercube(object):
    """
    Data structure representing a table (aka a Hypercube) within a document.
    The constructor uses the taxonomy to figure out what axes the table has,
    what line items are allowed within the table, what are the domains of
    each axis, etc. The constructed table is still empty until it is populated
    by storing Context objects, which act as keys to locate facts within the
    table.
    """
    def __init__(self, entry_point, table_name):
        """
        entry_point is a reference to the EntryPoint document instance this table
        belongs to.
        table_name is the name of this table within the solar taxonomy, for
        example: "solar:ProductIdentifierTable".
        Creates a table instance with an empty list of Contexts. Figures out
        the axes and allowed line items using the relationships from the EntryPoint.
        """
        self._table_name = table_name
        # self._axes is a dictionary where key is the axis name and value is the
        # axis Concept instance.
        self._axes = {}
        self._allowed_line_items = []
        # self.contexts stores a list of contexts that have been populated within
        # this table instance.
        self.contexts = []

        relationships = entry_point.relations
        # Use the relationships to find the names of my axes:
        for relation in relationships:
            if relation['role'] == 'hypercube-dimension':
                if relation['from'] == self._table_name:
                    axis_name = relation['to']
                    if not axis_name in self._axes:
                        concept = entry_point.getConceptByName(axis_name)
                        self._axes[axis_name] = Axis(concept)

        # If there's an arcrole of "all" then the "from" is a LineItems
        # and the "to" is the table?  I think?
        for relation in relationships:
            if relation['role'] == 'all':
                if relation['to'] == self._table_name:
                    line_item = relation['from']
                    if not self.hasLineItem(line_item):
                        self._allowed_line_items.append(line_item)

        # If there's dimension-domain or domain-member relationships for any
        # of my axes, extract that information as well:
        for relation in relationships:
            if relation['role'] == 'dimension-domain':
                if relation['from'] in self._axes:
                    domain = relation['to']
                    self._axes[ relation['from'] ].domain = domain

        for relation in relationships:
            if relation['role'] == 'domain-member':
                for axis in self._axes.values():
                    if axis.domain == relation['from']:
                        member = relation['to']
                        axis.domainMembers.append( member )
        

    def name(self):
        return self._table_name

    def axes(self):
        return self._axes.keys()

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
        # if not present, reutrn None? or throw exception?
        return self.getDomain(dimensionName) is not None

    def getDomain(self, dimensionName):
        axis = self._axes[dimensionName]
        if axis.domain is not None:
            return axis.domain
        
        concept = self._axes[dimensionName].concept
        domain_ref = concept.getMetadata("typed_domain_ref")
        
        if domain_ref is not None:
            # The typed_domain_ref metadata property will contain something like
            #    "#solar_ProductIdentifierDomain"  which is actually an internal link
            # to an ID inside the taxonomy XML document. I am making the assumption here
            # that it can be easily translated to an actual domain name by just replacing
            # "#solar_" with "solar": but a better approach would be to look up the element
            # matching the ID and read the name from that element.
            return domain_ref.replace("#solar_", "solar:")
        return None

    def axisValueWithinDomain(self, dimensionName, dimensionValue):
        # TODO make this a method of the Axis object?
        axis = self._axes[dimensionName]
        if axis.domain is not None:
            return dimensionValue in axis.domainMembers
        return False

    def sufficientContext(self, context):
        for axis_name in self._axes:
            if not axis_name in context.axes:
                raise Exception("Missing required {} axis for table {}".format(
                    axis_name, self._table_name))

            # Check that the value is not outside the domain, for domain-based axes:
            # (How do we do that?)
            axis = self._axes[axis_name]
            if axis.domain is not None:
                axis_value = context.axes[axis_name]
                if not axis_value in axis.domainMembers:
                    raise Exception("{} is not a valid value for the axis {}.".format(
                        axis_value, axis_name))

        for axis_name in context.axes:
            if not axis_name in self._axes:
                raise Exception("{} is not a valid axis for table {}.".format(
                    axis_name, self._table_name))



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

        self.id_scheme = "http://xbrl.org/entity/identification/scheme" #???

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
        """
        Adds this context to a hypercub
        """
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
    def __init__(self, concept, context, unit, value, decimals=2):
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
        self.unit = unit
        self.decimals = decimals

    def toXML(self):
        """
        Return the Fact as an XML element.
        """
        attribs = {"contextRef": self.context.get_id()}
        # TODO the "pure" part is probably wrong now.
        # also the self.unit may not be correct unitRef? not sure
        if self.unit is not None:
            attribs["unitRef"] = self.unit
            if self.unit == "pure" or self.unit == "degrees":
                attribs["decimals"] = "0"
            else:
                attribs["decimals"] = str(self.decimals)
        elem = Element(self.concept, attrib=attribs)
        if self.unit == "pure":
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
        if self.unit is not None:
            aspects["xbrl:unit"] = self.unit

        if isinstance( self.value, datetime.datetime):
            value_str = self.value.strftime("%Y-%m-%d")
        else:
            value_str = str(self.value)
        return { "aspects": aspects,
                 "value": value_str}


class Concept(object):
    """
    Represents metadata about concepts and their relationships:
    instances of this class are nodes in a tree data structure to keep track
    of which concepts are parents/children of other concepts in the schema hierarchy.
    Also stores concept metadata derived from the schema.
    """
    def __init__(self, taxonomy_semantic, concept_name):
        self.name = concept_name
        self.parent = None
        self.children = []

        try:
            self.metadata = taxonomy_semantic.concept_info(concept_name)
        except KeyError, e:
            print("Warning: no metadata found for {}".format(concept_name))


    def getMetadata(self, field_name):
        # concept_metadata properties:
        #x.period_type
        #x.nillable
        #x.id
        #x.name
        #x.substitution_group
        #x.type_name
        #x.period_independent
        # and sometimes:
        # x.typed_domain_ref
        # Which will be useful for validation.
        return getattr( self.metadata, field_name, None)

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
        self.tu = taxonomy.units
        self.entrypoint_name = entrypoint_name
        if not self.ts.validate_ep(entrypoint_name):
            raise Exception("There is no Orange Button entrypoint named {}."\
                                .format(entrypoint_name))

        # This gives me the list of every concept that could ever be
        # included in the document.

        self._all_my_concepts = {}
        for concept_name in self.ts.concepts_ep(entrypoint_name):
            if concept_name.endswith("_1"):
                # There are a bunch of duplicate concept names that all end in "_1"
                # that raise an exception if we try to query them.
                continue
            self._all_my_concepts[concept_name] = Concept(self.ts, concept_name)


        # Get the relationships (this comes from solar_taxonomy/documents/
        #  <entrypoint>/<entrypoint><version>_def.xml)
        self.relations = self.ts.relationships_ep(entrypoint_name)
        # Search through the relationships to find all of the tables, their
        # axes, and parent/child relationships between concepts:
        self._initialize_parents()
        self._initialize_tables()

        self.facts = {}
        self.namespaces = {
            "xmlns": "http://www.xbrl.org/2003/instance",
            "xmlns:link": "http://www.xbrl.org/2003/linkbase",
            "xmlns:xlink": "http://www.w3.org/1999/xlink",
            "xmlns:xsi": "http://www.w3.org/2001/XMRLSchema-instance",
            "xmlns:units": "http://www.xbrl.org/2009/utr",
            "xmlns:xbrldi": "http://xbrl.org/2006/xbrldi",
            "xmlns:solar": "http://xbrl.us/Solar/v1.2/2018-03-31/solar"
        }
        self.taxonomy = "https://raw.githubusercontent.com/xbrlus/solar/v1.2/core/solar_2018-03-31_r01.xsd"


    def _initialize_tables(self):
        """
        Uses relations to find all of the tables (hypercubes) allowed in
        the document, and the axes and lineitems for each one.
        """
        # When there's an arcrole of "hypercube-dimensions", the "from"
        # is a hypercube/table, and the "to" is an axis. Use these
        # relationships to find all of the hypercube
        self._tables = {}
        all_table_names = set([])
        for relation in self.relations:
            if relation['role'] == 'hypercube-dimension':
                table_name = relation['from']
                all_table_names.add(table_name)

        for table_name in all_table_names:
            self._tables[table_name] = Hypercube(self, table_name)


    def _initialize_parents(self):
        # Put the concepts into a tree based on domain-member
        # relations.
        for relation in self.relations:
            if relation['role'] == 'domain-member':
                parent_name = relation['from']
                child_name = relation['to']
                if parent_name.endswith("_1") or child_name.endswith("_1"):
                    # These are the duplicate concept names and are unwanted
                    continue
                parent = self.getConceptByName(parent_name)
                child = self.getConceptByName(child_name)
                parent.addChild(child)

    def getConceptByName(self, concept_name):
        return self._all_my_concepts[concept_name]

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
        if not concept_name in self._all_my_concepts:
            raise Exception("{} is not an allowed concept for {}".format(
                concept_name, self.entrypoint_name))
        # We know that a concept belongs in a table because the concept
        # is a descendant of a LineItem that has a relationship to the
        # table.
        ancestors = self._all_my_concepts[concept_name].getAncestors()
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
        if concept_name in self._all_my_concepts:
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
        period_type = self.getConceptByName(concept_name).getMetadata("period_type")

        if period_type == "duration":
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


        if period_type == "instant":
            if not context.instant:
                raise Exception("Missing required instant in {} context".format(
                    concept_name))
                # TODO check isinstance(instant, datetime)

        # If we got this far, we know the time period is OK. Now check the
        # required axes, if this concept is on a table:
        table = self.getTableForConcept(concept_name)
        if table is not None:
            table.sufficientContext(context)

        return True

    def validUnit(self, concept, unit_id):
        # TODO Refactor to move this logic inold to the Concept class?

        unitlessTypes = ["xbrli:integerItemType", "xbrli:stringItemType",
                         "xbrli:decimalItemType", "xbrli:booleanItemType",
                         "xbrli:dateItemType", "num:percentItemType",
                         "xbrli:anyURIItemType"]
        # There is type-checking we can do for these unitless types but we'll handle
        # it elsewhere
        
        required_type = self.getConceptByName(concept).getMetadata("type_name")
        if required_type in unitlessTypes:
            if unit_id is None:
                return True
            else:
                raise Exception("Unit {} given for unitless concept {} ({})".format(
                    unit_id, concept, required_type))

        if required_type.startswith("solar-types:"):
            print("I don't know how to validate {} yet, skipping for now".format(required_type))
            return True

        # TODO what other required_types might we get here?

        if unit_id is None:
            raise Exception("No unit given for concept {}, requires type {}".format(
                concept, required_type))

        unit = self.tu.unit(unit_id)
        if unit is None:
            raise Exception("There is no unit ID={} in the taxonomy.".format(unit_id))

        # TODO: utr.xml has unqualified type names, e.g. "frequencyItemType" and we're looking
        # for a qualified type name e.g. "num-us:frequencyItemType". Should we assume that if
        # it matches the part after the colon, then it's a match? Or do we need to validate the
        # fully-qualified name?
        if required_type.split(":")[-1] == unit.item_type:
            return True
        else:
            # TODO raise here?
            return False
        # Unit has fields: unit_id, unit_name, ns_unit, item_type,
        # item_type_date, symbol, definition, base_standard, status, version_date



    def set(self, concept, value, **kwargs):
        """
        Adds a fact to the document. The concept and the context
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
            unit = None
        if "precision" in kwargs:
            precision = kwargs.pop("precision")

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

        # Check unit type:
        if not self.validUnit(concept, unit):
            raise Exception("{} is an invalid unit type for {}".format(unit, concept))
        
        # TODO check datatype of given value against concept
        
        table = self.getTableForConcept(concept)

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
    
    def _makeUnitTag(self, unit_id):
        """
        Return an XML tag for a unit (such as kw, kwh, etc). Fact tags can
        reference this unit tag.
        """
        # See http://www.xbrl.org/utr/utr.xml
        unit = Element("unit", attrib={"id": unit_id})
        measure = SubElement(unit, "measure")
        measure.text = "units:{}".format(unit_id)
        # because http://www.xbrl.org/2009/utr is included as xmlns:units

        return unit


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

        facts = self.get_facts()
        required_units = set([fact.unit for fact in self.get_facts() \
                              if fact.unit is not None])
        for unit in required_units:
            # Add a unit tag defining each unit we want to reference:
            xbrl.append(self._makeUnitTag(unit))

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

