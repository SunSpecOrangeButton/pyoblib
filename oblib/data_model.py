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

"""Orange Button data model."""

import xml.etree.ElementTree
from xml.etree.ElementTree import Element, SubElement
import datetime
import json
from taxonomy import PeriodType
from six import string_types
import validator
import identifier

UNTABLE = "NON_TABLE_CONCEPTS"

class OBException(Exception):
    """
    Base class for Orange Button data validity exceptions.
    """
    def __init__(self, message):
        super(OBException, self).__init__(message)

class OBTypeException(OBException):
    """
    Raised if we try to set a concept to a value with an invalid data type
    """
    def __init__(self, message):
        super(OBTypeException, self).__init__(message)

class OBContextException(OBException):
    """
    Raised if we try to set a concept without sufficient Context fields
    """
    def __init__(self, message):
        super(OBContextException, self).__init__(message)

class OBConceptException(OBException):
    """
    Raised if we try to set a concept that can't be set in the current
    Entrypoint
    """
    def __init__(self, message):
        super(OBConceptException, self).__init__(message)

class OBNotFoundException(OBException):
    """
    Raised if we refer to a name that's not found in the taxonomy
    """
    def __init__(self, message):
        super(OBNotFoundException, self).__init__(message)

class OBUnitException(OBException):
    """
    Raised if we try to set a concept to a value with incorrect units
    """
    def __init__(self, message):
        super(OBUnitException, self).__init__(message)

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
                        concept = entry_point.get_concept(axis_name)
                        self._axes[axis_name] = Axis(concept)

        # If there's an arcrole of "all" then the "from" is a LineItems
        # and the "to" is the table?  I think?
        for relation in relationships:
            if relation['role'] == 'all':
                if relation['to'] == self._table_name:
                    line_item = relation['from']
                    if not self.has_line_item(line_item):
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
                for axis in list(self._axes.values()):
                    if axis.domain == relation['from']:
                        member = relation['to']
                        axis.domainMembers.append( member )
        

    def get_name(self):
        """Return table name."""
        return self._table_name

    def get_axes(self):
        """Return a list of strings which are the names of the table's axes."""
        return list(self._axes.keys())

    def has_line_item(self, line_item_name):
        """
        Return True if the given line_item_name (a string naming a concept)
        can be stored in this table.
        """
        return line_item_name in self._allowed_line_items

    def store_context(self, new_context):
        """
        new_context must be a Context object.
        If there is a matching Context stored in the table already, returns
        that one and makes no change to the table.
        Otherwise, a unique ID is assigned to the new context and it's stored.
        Either way, it returns a Context object with an ID and the returned
        context is the one that should be used.
        """
        for context in self.contexts:
            if context.equals_context(new_context):
                return context
        # For the ID, just use "HypercubeName_serialNumber":
        new_id = "%s_%d" % (self._table_name, len(self.contexts))
        new_context.set_id(self, new_id)
        self.contexts.append(new_context)
        return new_context

    def lookup_context(self, old_context):
        """
        old_context: a Context object.
        If there is a matching Context stored in the table already, returns
        that one; otherwise returns None.
        """
        for context in self.contexts:
            if context.equals_context(old_context):
                return context
        return None

    def _toXML(self):
        """
        Returns a list of XML tags representing all the contexts in the table,
        ready to be added to an ElementTree.
        """
        return [context._toXML() for context in self.contexts]

    def is_typed_dimension(self, dimensionName):
        """
        Returns True if the dimensionName (a string) is a dimension with a defined
        domain, as opposed to an explicit dimension.
        """
        # if not present, return None? or throw exception?
        return self.get_domain(dimensionName) is not None

    def get_domain(self, dimensionName):
        """
        Gets the domain name (the name of a Concept) corresponding to the named
        dimension, if that dimension is a typed dimension; otherwise returns None.
        """
        axis = self._axes[dimensionName]
        if axis.domain is not None:
            return axis.domain
        
        concept = self._axes[dimensionName].concept
        domain_ref = concept.get_details("typed_domain_ref")
        
        if domain_ref is not None:
            # The typed_domain_ref metadata property will contain something like
            #    "#solar_ProductIdentifierDomain"  which is actually an internal link
            # to an ID inside the taxonomy XML document. I am making the assumption here
            # that it can be easily translated to an actual domain name by just replacing
            # "#solar_" with "solar": but a better approach would be to look up the element
            # matching the ID and read the name from that element.
            return domain_ref.replace("#solar_", "solar:")
        return None

    def get_valid_values_for_axis(self, dimensionName):
        axis = self._axes[dimensionName]
        return axis.domainMembers

    def is_axis_value_within_domain(self, dimensionName, dimensionValue):
        """
        dimensionName: a string naming one of the dimensions of this table.
        dimensionValue: a string containing a proposed value for that dimension
        returns True if the given value is allowed in the given dimension, False
        otherwise.
        """
        # TODO make this a method of the Axis object?
        axis = self._axes[dimensionName]
        if len(axis.domainMembers) == 0:
            # If this is a domain axis but not an enumerated domain axis, then for
            # now we'll allow anything. For example, ProductIdentifierAxis has
            # ProductIdentiferDomain but the value is not restricted to an enumerated
            # type.  TODO: in the future is there more validation we can do on this
            # kind of axis?
            return True

        return dimensionValue in axis.domainMembers

    def validate_context(self, context):
        """
        context: a Context object
        returns True if the given context provides valid values for all axes required
        to store it in this table. Raises an exception if any axis is missing, or
        has an out-of-bound value, or if an axis is given that doesn't belong in
        this table.
        """
        for axis_name in self._axes:
            if not axis_name in context.axes:
                raise OBContextException(
                    "Missing required {} axis for table {}".format(
                        axis_name, self._table_name))

            # Check that the value is not outside the domain, for domain-based axes:
            axis = self._axes[axis_name]
            if self.is_typed_dimension(axis_name):
                axis_value = context.axes[axis_name]
                if not self.is_axis_value_within_domain(axis_name, axis_value):
                    raise OBContextException(
                        "{} is not a valid value for the axis {}.".format(
                        axis_value, axis_name))

        for axis_name in context.axes:
            if not axis_name in self._axes:
                raise OBContextException(
                    "{} is not a valid axis for table {}.".format(
                        axis_name, self._table_name))


class Context(object):
    """
    Represents the context for one or more facts. The context tells us
    when the fact applies, who is the entity reporting the fact, and also
    provides values for all of the table axes (aka Dimensions) needed to place
    the fact within a table (aka Hypercube). A fact cannot be reported without
    a context.
    """
    def __init__(self, **kwargs):
        """
        Keyword arguments accepted to constructor are:
        instant -- a period of instant type (e.g. a single datetime)
        duration -- a period of duration type: either a mini dictionary
                    with {"start": <date>, "end": <date>} fields, OR
                     the special string "forever"
        entity -- name of the entity making the report (e.g. business or other
                  enterprise)
        All other arguments aside from the above will be assumed to be the
        names of Axes. For example, an argument of:
        InverterPowerLevelPercentAxis = 'solar:InverterPowerLevel50PercentMember'
        indicates that the context is going into a Hypercube that has an
        InverterPowerLevelPercentAxis, and for this context the value of that axis
        is to be 'solar:InverterPowerLevel50PercentMember'
        (i.e. this context describes the case where the inverter power level is 50%)
        EITHER instant OR duration (not both) is required.
        """
        self.instant = None
        self.duration = None
        self.entity = None
        # kwargs must provide exactly one of instant or duration
        if PeriodType.instant.value in kwargs and PeriodType.duration.value in kwargs:
            raise OBContextException("Context given both instant and duration")
        if (PeriodType.instant.value not in kwargs) and (PeriodType.duration.value not in kwargs):
            raise OBContextException("Context not given either instant or duration")
        if PeriodType.instant.value in kwargs:
            self.instant = kwargs.pop(PeriodType.instant.value)
        if PeriodType.duration.value in kwargs:
            self.duration = kwargs.pop(PeriodType.duration.value)
        if "entity" in kwargs:
            self.entity = kwargs.pop("entity")
        # anything that's not instant/duration or entity must be an axis
        self.axes = {}
        for keyword in kwargs:
            if not keyword.endswith("Axis"):
                # TODO in the future we should use metadata to identify
                # what's an axis, not just look for the string "Axis".
                raise OBContextException("Context given invalid keyword {}".format(keyword))
            qualified_name = keyword
            if not qualified_name.startswith("solar:"):
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

        for axis_name, axis_value in list(self.axes.items()):
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
        Adds this context to a hypercube
        """
        self.hypercube = hypercube
        self._id = new_id

    def get_id(self):
        return self._id

    def _toXML(self):
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
            startDate.text = self.duration["start"].strftime("%Y-%m-%d")
            endDate = SubElement(period, "endDate")
            endDate.text = self.duration["end"].strftime("%Y-%m-%d")
        elif self.instant is not None:
            instant_elem = SubElement(period, PeriodType.instant.value)
            instant_elem.text = self.instant.strftime("%Y-%m-%d")


        # Extra dimensions:
        if len(self.axes) > 0:
            segmentElem = SubElement(entity, "segment")

        for dimension in self.axes:
            # First figure out if dimension is typed or untyped:

            if self.hypercube.is_typed_dimension(dimension):
                typedMember = SubElement(
                    segmentElem, "xbrldi:typedMember",
                    attrib = {"dimension": dimension})
                domainElem = self.hypercube.get_domain(dimension)
                domain = SubElement(typedMember, domainElem)
                domain.text = str(self.axes[dimension])

            else:
                # if it's not one of the above, then it's an explicit dimension:
                explicit = SubElement(segmentElem, "xbrldi:explicitMember", attrib={
                    "dimension": dimension
                    })
                explicit.text = str(self.axes[dimension])
        return context

    def _toJSON(self):
        """
        Returns context's entity, period, and extra dimensions as JSON dictionary
        object.
        """
        aspects = {"entity": self.entity}

        datefmt = "%Y-%m-%dT%H:%M:%S"
        if (self.duration is not None) and (self.duration != "forever"):
            aspects["period"] = "{}/{}".format(
                self.duration["start"].strftime(datefmt),
                self.duration["end"].strftime(datefmt)
                )
        elif self.instant is not None:
            aspects["period"] = self.instant.strftime(datefmt)

        for dimension in self.axes:
            # TODO is there a difference in how typed axes vs explicit axes
            # are represented in JSON?
            if self.hypercube.is_typed_dimension(dimension):
                value_str = self.axes[dimension]
            else:
                value_str = self.axes[dimension]
            aspects[dimension] = value_str

        return aspects


class Fact(object):
    """
    Represents a single XBRL Fact, linked to a context, that can be exported
    as either XML or JSON. A Fact provides a value for a certain concept within
    a certain context, and can optionally provide units and a precision.
    """
    def __init__(self, concept, context, unit, value, decimals=None, precision=None):
        """
        Concept is the field name - it must match the schema definition.
        Context is a reference to this fact's parent Context object.
        Units is a string naming the unit, for example "kWh"
        Value is a string, integer, or float.
        For numeric types only, precision OR decimals (not both) can be specified.
        Decimals is the number of digits past the decimal point; precision is
        the total number of significant digits.
        """
        # in case of xml the context ID will be rendered in the fact tag.
        # in case of json the contexts' attributes will be copied to the
        # fact's aspects.
        self.concept = concept
        self.value = value
        self.context = context
        self.unit = unit

        if decimals is not None and precision is not None:
            raise OBException("Fact given both precision and decimals - use only one.")
        self.decimals = decimals
        self.precision = precision
        if decimals is None and precision is None:
            # Default to 2 decimals:
            self.decimals = 2

        # Fill in the id property with a UUID:
        self.id = identifier.identifier() # Only used when exporting JSON

    def _toXML(self):
        """
        Return the Fact as an XML element.
        """
        attribs = {"contextRef": self.context.get_id(),
                   "id": self.id}
        # TODO the "pure" part is probably wrong now.
        # also the self.unit may not be correct unitRef? not sure
        if self.unit is not None:
            attribs["unitRef"] = self.unit
            if self.unit == "pure":
                attribs["decimals"] = "0"
            else:
                if self.decimals is not None:
                    attribs["decimals"] = str(self.decimals)
                elif self.precision is not None:
                    attribs["precision"] = str(self.precision)
        elem = Element(self.concept, attrib=attribs)
        if self.unit == "pure":
            elem.text = "%d" % self.value
        else:
            elem.text = str(self.value)
        return elem


    def _toJSON(self):
        """
        Return the Fact as a JSON dictionary object
        """
        aspects = self.context._toJSON()
        aspects["concept"] = self.concept
        if self.unit is not None:
            aspects["unit"] = self.unit
            if self.unit == "pure":
                aspects["decimals"] = "0"
            else:
                if self.decimals is not None:
                    aspects["decimals"] = str(self.decimals)
                elif self.precision is not None:
                    aspects["precision"] = str(self.precision)

        if isinstance( self.value, datetime.datetime):
            value_str = self.value.strftime("%Y-%m-%dT%H:%M:%S")
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
        """Concept constructor."""
        self.name = concept_name
        self.parent = None
        self.children = []

        try:
            self.metadata = taxonomy_semantic.get_concept_details(concept_name)
        except KeyError as e:
            print("Warning: no metadata found for {}".format(concept_name))


    def get_details(self, field_name):
        """
        Returns the concept metadata value for the named field, or None if there
        is no value for that field. Accepted field_names are:
        'period_type'
        'nillable'
        'id'
        'name'
        'substitution_group'
        'type_name'
        'period_independent'
        'typed_domain_ref' (only present for dimension concepts)
        """
        return getattr( self.metadata, field_name, None)

    def set_parent(self, new_parent):
        """Set a concept parent."""
        self.parent = new_parent
        if self not in self.parent.children:
            self.parent.children.append(self)

    def add_child(self, new_child):
        """Add a child concept."""
        if new_child not in self.children:
            self.children.append(new_child)
        new_child.parent = self

    def get_ancestors(self):
        """Returns a flat list of Concept instances, including the concept's
        parent, its parent's parent, etc. recursively up to the root of the tree."""
        ancestors = []
        curr = self
        while curr.parent is not None:
            ancestors.append(curr.parent)
            curr = curr.parent
        return ancestors

    def validate_datatype(self, value):
        """
        True if the given value matches the expected type of this concept.
        e.g. integer, string, decimal, boolean, or complex enumerated type.
        False otherwise.
        """
        return not validator.validate_concept_value(self.metadata, value)[1]
        myType = self.get_details("type_name")
        if myType == "xbrli:integerItemType":
            if isinstance(value, int):
                return True
            elif isinstance(value, string_types):
                try:
                    value = int( value )
                    return True
                except ValueError as e:
                    try:
                        # the case of "1.0" - string can't be converted to int
                        # but can be converted to float
                        value = float(value)
                        return int(value) == value
                    except ValueError as e:
                        return False
            return False
        if myType == "xbrli:stringItemType":
            return isinstance( value, string_types )
        if myType == "xbrli:booleanItemType":
            if isinstance( value, bool):
                return True
            if value in ["true", "false", "True", "False"]:
                return True
            return False
        
        if myType == "xbrli:decimalItemType":
            try:
                value = float( value )
            except ValueError as e:
                return False
            else:
                return True
        if myType == "xbrli:monetaryItemType":
            # TODO I assume this is the same as decimalItemType except that it
            # also requires a unit (units are validated elsewhere). Is this
            # correct?
            if isinstance( value, string_types ):
                value = value.replace("$", "")
                value = value.replace(",", "")
            try:
                value = float( value )
            except ValueError as e:
                return False
            else:
                return True
        if myType == "xbrli:dateItemType":
            if isinstance( value, datetime.date):
                return True
            if isinstance( value, datetime.datetime):
                return True
            if isinstance( value, string_types):
                # also return true if it's a string that can be parsed into
                # a date according to a standard pattern. Note that this assumes
                # American style month-first date; LONGTERM TODO support multiple
                # date formats. Also LONGTERM TODO we may need to convert this
                # into a date object instead of just returning true/false.
                date_formats = ["%m/%d/%y", "%m/%d/%Y"]
                success = False
                for fmt in date_formats:
                    try:
                        converted_val = datetime.datetime.strptime(value, fmt)
                    except ValueError as e:
                        continue
                    else:
                        success = True
                return success
            return False
        if myType == "num:percentItemType":
            # TODO Look up what is expected -- does this want 0.01 - 0.99 or
            # does it want 1 - 99  or does it want "1%" - "99%" ?
            return True
        if myType == "xbrli:anyURIItemType":
            # TODO there's probably a validation method in urllib or something
            # that we can import here.
            return True
        print("Warning: i don't know how to validate " + myType)

        # TODO add validation for complex types.  Most types in the num:
        # namespace will be decimals that expect units. Most types in
        # the solar-types: namespace will be enumerated string types.
        return True



class OBInstance(object):
    """
    Data structure representing an entrypoint.

    A data structure representing an orange button document
    from a particular entrypoint -- for example, an MOR.
    This class's representation of the data is format-agnostic, it just
    provides methods for getting/setting and validation; translation to
    and from particular physical file format (or database schema) will
    be handled elsewhere.
    """
    def __init__(self, entrypoint_name, taxonomy, dev_validation_off=False):
        """
        Initialize an entrypoint.

        Initializes an empty instance of a document corresponding to the named
        entrypoint. entrypoint_name is a string that must match an entry point
        in the taxonomy. Looks up the list of concepts for this entry point
        from the taxonomy to know what concepts are allowed in the document.
        Looks up the relationships between concepts for this entry point from
        the taxonomy to know the hierarchical relationship of concepts, tables,
        and axes/dimensions.
        taxonomy_semantic should be the global singleton TaxonomySemantic
        object.

        An optional flag ("dev_validation_off") can be set to turn validation
        rules off during development.  This should not be used during a release.   
        """
        self.ts = taxonomy.semantic
        self.tu = taxonomy.units
        self.entrypoint_name = entrypoint_name
        self._dev_validation_off = dev_validation_off

        if entrypoint_name == "All":
            self._init_all_entrypoint()
        else:
            if not self.ts.is_entrypoint(entrypoint_name):
                raise OBNotFoundException(
                    "There is no Orange Button entrypoint named {}.".format(
                        entrypoint_name))

            # This gives me the list of every concept that could ever be
            # included in the document.
            self._all_my_concepts = {}
            for concept_name in self.ts.get_entrypoint_concepts(entrypoint_name):
                if concept_name.endswith("_1"):
                    # There are a bunch of duplicate concept names that all end in "_1"
                    # that raise an exception if we try to query them.
                    continue
                self._all_my_concepts[concept_name] = Concept(self.ts, concept_name)

            # Get the relationships (this comes from solar_taxonomy/documents/
            #  <entrypoint>/<entrypoint><version>_def.xml)
            self.relations = self.ts.get_entrypoint_relationships(entrypoint_name)

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
            # TODO add usgaap here, if any concepts start with usgaap?
        }
        self.taxonomy_name = "https://raw.githubusercontent.com/xbrlus/solar/v1.2/core/solar_2018-03-31_r01.xsd"
        self._default_context = {}

    def _init_all_entrypoint(self):
        # take every concept from taxonomy
        every_concept = []
        for x in self.ts._concepts.values():
            every_concept.extend(x)

        self._all_my_concepts = {}
        for concept_name in every_concept:
            self._all_my_concepts[concept_name] = Concept(self.ts, concept_name)
        # Take every relation from taxonomy

        every_relation = []
        for x in self.ts._relationships.values():
            every_relation.extend(x)
        self.relations = every_relation  # this will contain a lot of duplicates
        # can't do list(set(list)) when the starting point is a list of dicts
        # since dicts aren't trivially comparable


    def _initialize_tables(self):
        """
        Find tables.

        Use relations to find all of the tables (hypercubes) allowed in
        the document, and the axes and lineitems for each one.
        """
        # When there's an arcrole of "hypercube-dimensions", the "from"
        # is a hypercube/table, and the "to" is an axis. Use these
        # relationships to find all hypercube names.
        self._tables = {}
        all_table_names = set([])
        for relation in self.relations:
            if relation['role'] == 'hypercube-dimension':
                table_name = relation['from']
                all_table_names.add(table_name)

        for table_name in all_table_names:
            self._tables[table_name] = Hypercube(self, table_name)


    def _initialize_parents(self):
        """Put the concepts into a tree based on domain-member relations."""
        for relation in self.relations:
            if relation['role'] == 'domain-member':
                parent_name = relation['from']
                child_name = relation['to']
                if parent_name.endswith("_1") or child_name.endswith("_1"):
                    # These are the duplicate concept names and are unwanted
                    continue
                parent = self.get_concept(parent_name)
                child = self.get_concept(child_name)
                parent.add_child(child)

    def get_concept(self, concept_name):
        """
        Returns the Concept instance object matching given concept_name string.
        """
        return self._all_my_concepts[concept_name]

    def get_table_names(self):
        """
        Returns a list of strings identifying all tables that can be included
        in this document.
        """
        return list(self._tables.keys())

    def get_table(self, table_name):
        """
        Returns the Table instance matching the given table_name string, if it
        is present in this document.
        """
        return self._tables[table_name]

    def _identify_relations(self, concept_name):
        # Development method for listing all relationships for debugging
        # purposes. Do not use in production.
        from_me = [r for r in self.relations if r['from'] == concept_name]
        for x in from_me:
            print("{} -> {} -> {}".format(concept_name, x['role'], x['to']))
        to_me = [r for r in self.relations if r['to'] == concept_name]
        for x in to_me:
            print("{} -> {} -> {}".format(x['from'], x['role'], concept_name))

    def get_table_for_concept(self, concept_name):
        """
        Returns the table for a concept.

        Given a concept_name, returns the table (Hypercube object) which
        that concept belongs inside of, or None if there's no match.
        """
        if concept_name not in self._all_my_concepts:
            raise OBConceptException(
                "{} is not an allowed concept for {}".format(
                    concept_name, self.entrypoint_name))
        # We know that a concept belongs in a table because the concept
        # is a descendant of a LineItem that has a relationship to the
        # table.
        ancestors = self._all_my_concepts[concept_name].get_ancestors()
        for ancestor in ancestors:
            if "LineItem" in ancestor.name: # maybe not????
                for table in list(self._tables.values()):
                    if table.has_line_item(ancestor.name):
                        return table

        # print "Warning: no table for {}, writing it to default table".format(concept_name)
        # kind of a hack here -- make a placeholder table with no axes for the non-table concepts
        if not UNTABLE in self._tables:
            self._tables[UNTABLE] = Hypercube(self, UNTABLE)
        return self._tables[UNTABLE]

    def get_all_writable_concepts(self):
        """
        Return list of strings naming all concepts that can be written to this
        document.
        """
        return [c for c in self._all_my_concepts if self.is_concept_writable(c)]

    def is_concept_writable(self, concept_name):
        """
        Return whether a concept is writable.

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

    def validate_context(self, concept_name, context):
        """
        True if the given Context object contains all the information
        needed to provide full context for the named concept -- sufficient
        time period information (duration/instant), sufficient axes to place
        the fact within its table, etc.
        Otherwise, raises an exception explaining what is wrong.
        """
        # TODO Refactor to put this logic into the Concept?
        period_type = self.get_concept(concept_name).get_details("period_type")

        if PeriodType(period_type) == PeriodType.duration:
            if not context.duration:
                raise OBContextException(
                    "Missing required duration in {} context".format(
                        concept_name))

            # a valid duration is either "forever" or {"start", "end"}
            valid = False
            if context.duration == "forever":
                valid = True
            if "start" in context.duration and "end" in context.duration:
                # TODO check isinstance(duration["start"], datetime)
                valid = True
            if not valid:
                raise OBContextException(
                    "Invalid duration in {} context".format(
                        concept_name))


        if PeriodType(period_type) == PeriodType.instant:
            if not context.instant:
                raise OBContextException(
                    "Missing required instant in {} context".format(
                        concept_name))
                # TODO check isinstance(instant, datetime)

        # If we got this far, we know the time period is OK. Now check the
        # required axes, if this concept is on a table:
        table = self.get_table_for_concept(concept_name)
        if table is not None:
            table.validate_context(context)

        return True

    def _is_valid_unit(self, concept, unit_id):
        # TODO Refactor to move this logic into the Concept class?

        unitlessTypes = ["xbrli:integerItemType", "xbrli:stringItemType",
                         "xbrli:decimalItemType", "xbrli:booleanItemType",
                         "xbrli:dateItemType", "num:percentItemType",
                         "xbrli:anyURIItemType"]
        # There is type-checking we can do for these unitless types but we'll handle
        # it elsewhere
        
        required_type = self.get_concept(concept).get_details("type_name")
        if required_type in unitlessTypes:
            if unit_id is None:
                return True
            else:
                raise OBUnitException(
                    "Unit {} given for unitless concept {} ({})".format(
                        unit_id, concept, required_type))

        if required_type.startswith("solar-types:"):
            print("I don't know how to validate {} yet, skipping for now".format(required_type))
            return True

        # TODO what other required_types might we get here?

        if unit_id is None:
            raise OBUnitException(
                "No unit given for concept {}, requires type {}".format(
                    concept, required_type))

        unit = self.tu.is_unit2(unit_id)
        if unit is None:
            raise OBNotFoundException(
                "There is no unit ID={} in the taxonomy.".format(unit_id))

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


    def set(self, concept_name, value, **kwargs):
        """
        Adds a fact to the document. The concept_name and the context
        together identify the fact to set, and the value will be stored for
        that fact.
        If concept_name and context are identical to a previous call, the old fact
        will be overwritten. Otherwise, a new fact is created.
        accepts keyword args:
        context = a Context object
        unit_name = a string naming a unit
        precision = <number of significant digits of precision>(for decimal values only)
        decimals = <number of places past the decimal pt>(for decimal values only)
        (only one of precision or decimals should be given. Defaults to decimals=2)

        Alternately, the following can be supplied as separate keyword args instead of
        as a context object:
        duration = "forever" or {"start": <date>, "end": <date>}
        instant = <date>
        entity = <entity name>
        *Axis = <value>  (the name of any Axis in a table in this entrypoint)
        """

        if "unit_name" in kwargs:
            unit_name = kwargs.pop("unit_name")
            valid_unit_name = self.tu.is_unit(unit_name=unit_name)
        else:
            unit_name = None

        if "precision" in kwargs:
            precision = kwargs.pop("precision")
        else:
            precision = None
        if "decimals" in kwargs:
            decimals = kwargs.pop("decimals")
        else:
            decimals = None

        if not self.is_concept_writable(concept_name):
            raise OBConceptException(
                "{} is not a writeable concept".format(concept_name))
        concept = self.get_concept(concept_name)

        if "context" in kwargs:
            context = kwargs.pop("context")
        elif len(list(kwargs.keys())) > 0:
            # turn the remaining keyword args into a Context object -- this
            # is just syntactic sugar to make this method easier to call.
            period = concept.get_details("period_type")
            if period not in kwargs and period in self._default_context:
                kwargs[period.value] = self._default_context[period]
            context = Context(**kwargs)
        else:
            context = None

        # Use default values, if any have been set, to fill in missing fields of context:
        if len(self._default_context) > 0:
            context = self._fill_in_context_from_defaults(context, concept)

        if not self.validate_context(concept_name, context):
            raise OBContextException(
                "Insufficient context for {}".format(concept_name))

        # Check unit type:
        if not self._dev_validation_off and not self._is_valid_unit(concept_name, unit_name):
            raise OBUnitException(
                "{} is an invalid unit type for {}".format(unit_name, concept_name))
        
        # check datatype of given value against concept
        if not self._dev_validation_off and not concept.validate_datatype(value):
            raise OBTypeException(
                "{} is the wrong datatype for {}".format(value, concept_name))

        
        table = self.get_table_for_concept(concept_name)
        context = table.store_context(context) # dedupes, assigns ID

        f = Fact(concept_name, context, unit_name, value,
                 precision=precision,
                 decimals=decimals)

        # self.facts is nested dict keyed first on table then on context ID
        # and finally on concept:
        if not table.get_name() in self.facts:
            self.facts[table.get_name()] = {}
        if not context.get_id() in self.facts[table.get_name()]:
            self.facts[table.get_name()][context.get_id()] = {}
        # TODO simplify above with defaultdict
        
        self.facts[table.get_name()][context.get_id()][concept_name] = f
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

        # TODO if only some fields of the context are given, try matching
        # on just those fields and disregarding the rest -- e.g. if no
        # period is given, return a fact that matches the other fields, whatever
        # its duration is?

        # TODO a function that returns multiple, i.e. all facts for given
        # concept regardless of context, or vice versa.
        table = self.get_table_for_concept(concept)
        context = table.lookup_context(context)
        if table.get_name() in self.facts:
            if context.get_id() in self.facts[table.get_name()]:
                if concept in self.facts[table.get_name()][context.get_id()]:
                    return self.facts[table.get_name()][context.get_id()][concept]
        return None

    def get_all_facts(self):
        """
        Returns a flattened list of Fact instances -- all of the facts that
        have been set in this document so far.
        """
        all_facts = []
        for table_dict in list(self.facts.values()):
            for context_dict in list(table_dict.values()):
                for fact in list(context_dict.values()):
                    all_facts.append(fact)
        return all_facts
    
    def _make_unit_tag(self, unit_id):
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


    def _toXML_tag(self):
        """
        Returns an XML tag which is the root of an XML tree representing
        the entire document contents (all contexts, units, and facts) in XML form.
        """
        # The root element:
        xbrl = Element("xbrl", attrib = self.namespaces)

        # Add "link:schemaRef" for the taxonomy that goes with this document:
        link = SubElement(xbrl, "link:schemaRef",
                          attrib = {"xlink:href": self.taxonomy_name,
                                    "xlink:type": "simple"})

        # Add a context tag for each context we want to reference:
        for hypercube in list(self._tables.values()):
            tags = hypercube._toXML()
            for tag in tags:
                xbrl.append(tag)

        facts = self.get_all_facts()
        required_units = set([fact.unit for fact in self.get_all_facts() \
                              if fact.unit is not None])
        for unit in required_units:
            # Add a unit tag defining each unit we want to reference:
            xbrl.append(self._make_unit_tag(unit))

        for fact in self.get_all_facts():
            xbrl.append( fact._toXML() )

        return xbrl

    def to_XML(self, filename):
        """
        Exports XBRL as XML to the given filename.

        To ensure future support use the method with the same name and functionality in Parser.
        """
        xbrl = self._toXML_tag()
        tree = xml.etree.ElementTree.ElementTree(xbrl)
        # Apparently every XML file should start with this, which ElementTree
        # doesn't do:
        # <?xml version="1.0" encoding="utf-8"?>
        tree.write(filename)

    def to_XML_string(self):
        """
        Returns XBRL as an XML string.

        To ensure future support use the method with the same name and functionality in Parser.
        """
        xbrl = self._toXML_tag()
        return xml.etree.ElementTree.tostring(xbrl).decode()


    def to_JSON(self, filename):
        """
        Exports XBRL as JSON to the given filename.

        To ensure future support use the method with the same name and functionality in Parser.
        """

        outfile = open(filename, "w")
        outfile.write(self.to_JSON_string())
        outfile.close()

    def to_JSON_string(self):
        """
        Returns XBRL as a JSON string

        To ensure future support use the method with the same name and functionality in Parser.
        """
        masterJsonObj = {
            "documentType": "http://www.xbrl.org/WGWD/YYYY-MM-DD/xbrl-json",
            "prefixes": self.namespaces,
            "dtsReferences": [],
            "facts": {}
            }

        masterJsonObj["dtsReferences"].append({
            "type": "schema",
            "href": self.taxonomy_name
        })

        facts = self.get_all_facts()

        for fact in facts:
            masterJsonObj["facts"][fact.id] = fact._toJSON()
        return json.dumps(masterJsonObj)

    def set_default_context(self, dictionary):
        """
        Dictionary can have keys: "entity", PeriodType.instant, PeriodType.duration, and also
        axes.
        Sets these values as the defaults for this document. These values
        are used to fill in any fields that are missing from any contexts
        passed into set(). For example, if you set the "entity" as a default
        on the document, then after that you can leave "entity" out of your
        contexts and the default entity will be used.
        """
        self._default_context.update(dictionary)

    def _fill_in_context_from_defaults(self, context, concept):
        """
        context: None, or a Context object that may be missing some fields
        concept: a Concept object (used to determine what fields are required)
        Returns a Context object that has had all its required fields filled in
        from the default context (see set_default_context()) if possible.
        """
        period = concept.get_details("period_type") # PeriodType.instant or PeriodType.duration
        if context is None:
            # Create context from default entity and default period:
            context_args = {}
            if period in self._default_context:
                context_args[period.value] = self._default_context[period]
            else:
                raise OBContextException(
                    "{} needs a {}, no default set and no context given.".format(
                        concept.name, period.value))
            if "entity" in self._default_context:
                context_args["entity"] = self._default_context["entity"]
            context = Context(**context_args)

        else:
            # If entity or period is missing, fill in from defaults:
            if context.entity is None and "entity" in self._default_context:
                context.entity = self._default_context["entity"]

            if getattr(context, period.value, None) is None and period in self._default_context:
                setattr( context, period.value, self._default_context[period] )

        # If any axis that the table wants is missing, fill in axis from defaults:
        table = self.get_table_for_concept(concept.name)
        if table is not None:
            for axis_name in table.get_axes():
                if axis_name in self._default_context and axis_name not in context.axes:
                    context.axes[axis_name] = self._default_context[axis_name]
        return context

    def is_valid(self):
        """
        (Placeholder).

        Returns true if all of the facts in the document validate.
        i.e. they have allowed data types, allowed units, anything that needs
        to be in a table has all the required axis values to identify its place
        in that table, etc.
        """
        return True

    def is_complete(self):
        """
        (Placeholder).

        (Placeholder) Returns true if no required facts are missing, i.e. if
        there is a value for all concepts with nillable=False
        """
        return True
