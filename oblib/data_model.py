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

""" Orange Button data model.

Consists of

- :py:class:`OBInstance`, representing an XBRL Instance Document
- :py:class:`Concept`, representing a XBRL concept
- :py:class:`Fact`, representing a XBRL fact
- :py:class:`Context`, representing the XBRL context for a fact
- :py:class:`Axis` and :py:class:`Hypercube` to represent tables within Instance Documents.

If you are writing Orange Button, the typical usage is to create an `OBInstance`
document ``doc = OBInstance()`` and use ``doc.set`` to add data to the document,
and ``doc.to_XML_string`` or ``doc.to_JSON_string`` to export to the desired format.

Example:
::
    from oblib.taxonomy import getTaxonomy, PeriodType
    from oblib.data_model import OBInstance
    taxonomy = getTaxonomy()
    mor_document = OBInstance("MonthlyOperatingReport", taxonomy)
    mor_document.set_default_context({"entity": "My Company Name",
                                      PeriodType.duration: "forever"})
    mor_document.set("solar:MonthlyOperatingReportEffectiveDate",
                     date(year=2018, month=12, day=1))
    mor_document.set("solar:MeasuredEnergy", "1246.25", unit_name="kWh")
    xml = mor_document.to_XML_string()
::

If you are reading Orange Button data, the typical usage is to read the source
JSON or XML file with ``oblib.Parser`` to create an ``OBInstance`` document,
then use the document's ``.get`` method to read data from  the document.

"""

import xml.etree.ElementTree
from xml.etree.ElementTree import Element, SubElement
import datetime
import json
from six import string_types
from oblib import taxonomy, validator, identifier
from oblib.ob import (
    OBError, OBTypeError, OBContextError,
    OBConceptError, OBNotFoundError,
    OBValidationError, OBUnitError)

UNTABLE = "NON_TABLE_CONCEPTS"


class Hypercube(object):
    """
    Data structure representing a table (aka a Hypercube) within a document.
    The constructor uses the taxonomy to figure out what axes the table has,
    what line items are allowed within the table, what are the domains of
    each axis, etc. The constructed table is still empty until it is populated
    by storing Context objects, which act as keys to locate facts within the
    table.
    """
    def __init__(self, ob_instance, table_name):
        """
        Constructs a Hypercube instance with an empty list of Contexts. Figures out
        the axes and allowed line items using the relationships from the OBInstance.

        Args:
          ob_instance: reference to OBInstance instance
            the OBInstance that this table belongs to.
          table_name: string
            name of the table within the solar taxonomy, e.g.: "solar:ProductIdentifierTable".
        """

        self._table_name = table_name
        # self._axes is a dictionary where key is the axis name and value is the
        # axis Concept instance.
        self._axes = {}
        self._allowed_line_items = []
        # self.contexts stores a list of contexts that have been populated within
        # this table instance.
        self.contexts = []
        self.ts = ob_instance.ts

        relationships = ob_instance.relations
        # Use the relationships to find the names of my axes:
        for relation in relationships:
            if relation.role == taxonomy.RelationshipRole.hypercube_dimension:
                if relation.from_ == self._table_name:
                    axis_name = relation.to
                    if not axis_name in self._axes:
                        if not isinstance( ob_instance.get_concept(axis_name), Axis):
                            raise OBError(
                                "Expected {} to be an Axis instance but it isn't"\
                                .format(axis_name))
                        self._axes[axis_name] = ob_instance.get_concept(axis_name)

        # If there's an arcrole of "all" then the "from" is a LineItems
        # and the "to" is the table?  I think?
        for relation in relationships:
            if relation.role == taxonomy.RelationshipRole.dimension_all:
                if relation.to == self._table_name:
                    line_item = relation.from_
                    if not self.has_line_item(line_item):
                        self._allowed_line_items.append(line_item)

        # If there's dimension-domain or domain-member relationships for any
        # of my axes, extract that information as well:
        for relation in relationships:
            if relation.role == taxonomy.RelationshipRole.dimension_domain:
                if relation.from_ in self._axes:
                    domain = relation.to
                    self._axes[ relation.from_ ].domain = domain

        for relation in relationships:
            if relation.role == taxonomy.RelationshipRole.domain_member:
                for axis in list(self._axes.values()):
                    if axis.domain == relation.from_:
                        member = relation.to
                        axis.domainMembers.append( member )

    def get_name(self):
        """
        Returns:
          The name of the table, a string
        """
        return self._table_name

    def get_axes(self):
        """
        Returns:
          A list of strings which are the names of the table's axes.
        """
        return list(self._axes.keys())

    def has_line_item(self, line_item_name):
        """
        Args:
          line_item_name: string
            Name of a concept which may or may not be a line item
        Returns:
           True if the given line_item_name is a line itme which can be stored
           in this table.
        """
        return line_item_name in self._allowed_line_items

    def store_context(self, new_context):
        """
        De-duplicates a Context to avoid storing duplicate contexts in the table.
        Args:
          new_context: a Context instance
        Returns:
          A Context object with an ID that client code should use.
          If there is a matching Context stored in the table already, returns
          that one and makes no change to the table.
          Otherwise, a unique ID is assigned to the new context and it's both
          stored and returned.
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
        Args:
          old_context: a Context instance
        Returns:
          If there is a matching Context stored in the table already, returns
          that one; otherwise returns None.
        """
        for context in self.contexts:
            if context.equals_context(old_context):
                return context
        return None

    def _toXML(self):
        """
        Returns:
          a list of XML tags representing all the contexts in the table,
          ready to be added to an ElementTree.
        """
        return [context._toXML() for context in self.contexts]

    def is_typed_dimension(self, dimensionName):
        """
        Args:
          dimensionName: string
            name of a dimension (aka an Axis concept) which is an axis of this table
        Returns:
          True if the dimensionName (a string) is a dimension with a defined
          domain, as opposed to an explicit dimension.
        """
        # TODO if not present, return False? or throw exception?
        return self.get_domain(dimensionName) is not None

    def get_domain(self, dimensionName):
        """
        Args:
          dimensionName: string
            name of a dimension (aka an Axis concept) which is an axis of this table
        Returns:
          The domain name (a string, name of a Concept) corresponding to the named
          dimension, if that dimension is a typed dimension; otherwise returns None.
        """
        axis = self._axes[dimensionName]
        return axis.get_domain()


    def get_valid_values_for_axis(self, dimensionName):
        """
        Args:
          dimensionName: string
            name of a dimension (aka an Axis concept) which is an axis of this table
        Returns:
          if this axis is restricted to certain values (an enumerated type), returns
          a list of strings where each string is a valid value (the name of a
          Member-type concept)
          Otherwise, returns empty list.
        """

        axis = self._axes[dimensionName]
        return axis.domainMembers

    def is_axis_value_within_domain(self, dimensionName, dimensionValue):
        """
        Args:
          dimensionName: string
            name of a dimension (aka an Axis concept) which is an axis of this table
          dimensionValue: a string containing a proposed value for that dimension
        Returns:
          True if the given value is allowed in the given dimension, False
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

    def _is_valid_context(self, context):
        """
        Args:
          context: a Context instance
            the context to be validated.
        Returns:
          None
        Raises:
          an OBContextError if any axis is missing, or has an out-of-bound value,
          or if an axis is given that doesn't belong in this table.
        """
        if not isinstance(context, Context):
            raise OBContextError("{} is not a valid Context instance".format(context))

        for axis_name in self._axes:
            if self.ts.get_concept_details(axis_name).typed_domain_ref and not axis_name in context.axes:
                raise OBContextError(
                    "Missing required {} axis for table {}".format(
                        axis_name, self._table_name))
            elif not self.ts.get_concept_details(axis_name).typed_domain_ref and not axis_name in context.axes:
                continue

            # Check that the value is not outside the domain, for domain-based axes:
            axis = self._axes[axis_name]
            if self.is_typed_dimension(axis_name):
                axis_value = context.axes[axis_name]
                if not self.is_axis_value_within_domain(axis_name, axis_value):
                    raise OBContextError(
                        "{} is not a valid value for the axis {}.".format(
                        axis_value, axis_name))

        for axis_name in context.axes:
            if not axis_name in self._axes:
                raise OBContextError(
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
        Constructs a Context object from keyword arguments. A context must have
        EITHER an instant OR a duration, but not both.
        Keyword Args:
          instant: datetime
            A period of instant type (e.g. a single datetime)
          duration: a dict with start and end fields {"start": <date>, "end": <date>}
            OR the literal string "forever" if there's no limit to the duration.
          entity: string
            Name of the entity making the report (e.g. business or other enterprise)
          <axis name>: <axis value>
            All other keyword arguments aside from instant, duration, and entity are
            assumed to be names of axes required by the table. For example, a kwarg like:
            InverterPowerLevelPercentAxis = 'solar:InverterPowerLevel50PercentMember'
            indicates that the context is going into a Hypercube that has an
            InverterPowerLevelPercentAxis, and for this context the value of that axis
            is to be 'solar:InverterPowerLevel50PercentMember'
            (i.e. this context describes the case where the inverter power level is 50%)
        Raises:
          OBContextError if required fields are missing or if conflicting fields are
          given.
        """
        self.instant = None
        self.duration = None
        self.entity = None
        # kwargs must provide exactly one of instant or duration
        if taxonomy.PeriodType.instant.value in kwargs and taxonomy.PeriodType.duration.value in kwargs:
            raise OBContextError("Context given both instant and duration")
        if (taxonomy.PeriodType.instant.value not in kwargs) and (taxonomy.PeriodType.duration.value not in kwargs):
            raise OBContextError("Context not given either instant or duration")
        if taxonomy.PeriodType.instant.value in kwargs:
            self.instant = kwargs.pop(taxonomy.PeriodType.instant.value)
        if taxonomy.PeriodType.duration.value in kwargs:
            self.duration = kwargs.pop(taxonomy.PeriodType.duration.value)
        if "entity" in kwargs:
            self.entity = kwargs.pop("entity")
        # anything that's not instant/duration or entity must be an axis
        self.axes = {}
        for keyword in kwargs:
            if not keyword.endswith("Axis"):
                raise OBContextError("Context given invalid keyword {}".format(keyword))
            qualified_name = keyword
            # Add solar: namespace iff no namespace is present.
            if ":" not in qualified_name:
                qualified_name = "solar:" + keyword
            self.axes[qualified_name] = kwargs[keyword]

        self.id_scheme = "http://xbrl.org/entity/identification/scheme" #???

    def equals_context(self, other_context):
        """
        Args:
          other_context: a Context object
        Returns:
          True if all my fields are the same as the fields in other_context.
        """
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
        Adds this context to a hypercube and sets its ID. (A context ID is only
        meaningful within a certain hypercube)
        Args:
          hypercube: reference to a Hypercube instance
            the given hypercube instance becomes the parent of this context
          new_id: string
            this context's ID becomes the given ID.
        Returns:
          None
        """
        self.hypercube = hypercube
        self._id = new_id

    def get_id(self):
        """
        Returns:
          This context's ID (a string)
        """
        return self._id

    def _toXML(self):
        """
        Returns: an XML Element representing this context and all its fields in
        XBRL XML format.
        """
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
            instant_elem = SubElement(period, taxonomy.PeriodType.instant.value)
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
        Returns:
          A JSON-style dictionary object containing this context's fields
          (entity, period, and extra dimensions).
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
                value_str = str(self.axes[dimension])
            else:
                value_str = str(self.axes[dimension])
            aspects[dimension] = value_str

        return aspects


class Fact(object):
    """
    Represents a single XBRL Fact, linked to a context, that can be exported
    as either XML or JSON. A Fact provides a value for a certain concept within
    a certain context, and can optionally provide units and a precision.
    """
    def __init__(self, concept_name, context, unit, value, decimals=None, precision=None, id=None):
        """
        Constructs a Fact instance.
        Args:
          concept_name: string
            name of an XBRL concept defined in the schema.
          context: reference to a Context object
            the given object becomes the parent context of this Fact.
          unit: string
            name of the unit in which a the value is expressed, for numeric values.
            for example "kWh" for kilowatt-hours. Must match a unit defined in the
            schema.
          value: string, integer, boolean, or float
            value of the fact. (i.e. value for given concept within given context)
          decimals: integer
            optional. For numeric types, the number of digits past the decimal point
            that are to be considered valid. Defaults to 2, i.e. value is precise to
            2 digits past decimal point.
          precision: integer
            optional. For numeric types, the total number of significant digits.
            EITHER precision OR decimals can be specified, not both.
          id: string
            optional, if included the fact id is set accordingly, otherwise it is
            auto-generated.
        Raises:
          OBError if constructor is given conflicting information
        """
        # in case of xml the context ID will be rendered in the fact tag.
        # in case of json the contexts' attributes will be copied to the
        # fact's aspects.
        self.concept_name = concept_name
        self.value = value
        self.context = context
        self.unit = unit

        if decimals is not None and precision is not None:
            raise OBError("Fact given both precision and decimals - use only one.")
        self.decimals = decimals
        self.precision = precision
        # FUTURE TODO: decide if the Concept is numeric or non-numeric. If numeric,
        # either require a decimals/precision or provide a default. If non-numeric,
        # don't allow decimals/precision to be set.

        # Fill in the id property with a UUID:
        if id is None:
            self.id = identifier.identifier()
        else:
            self.id = id

    def set_id(self, new_id):
        """
        Args:
          new_id: string
            The ID of this Fact becomes the new_id.
        """
        self.id = new_id

    # FUTURE TODO: setters and getters for concept, value, context, unit?

    def _toXML(self):
        """
        Returns:
          an XML element representing this Fact and all its fields in XBRL
          XML format.
        """
        attribs = {"contextRef": self.context.get_id(),
                   "id": self.id}
        # TODO the self.unit may not be correct unitRef? not sure
        if self.unit is not None:
            attribs["unitRef"] = self.unit
            if self.decimals is not None:
                attribs["decimals"] = str(self.decimals)
            elif self.precision is not None:
                attribs["precision"] = str(self.precision)
        elem = Element(self.concept_name, attrib=attribs)
        if self.unit == "pure":
            elem.text = "%d" % self.value
        else:
            elem.text = str(self.value)
        return elem

    def _toJSON(self):
        """
        Returns:
          a JSON-style dict representing this Fact and all its fields in XBRL
          JSON format. All values are strings except for True, False, and None
          which are literals. (see issue #142)
        """
        aspects = self.context._toJSON()
        aspects["concept"] = self.concept_name
        if self.unit is not None:
            aspects["unit"] = str(self.unit)
            if self.decimals is not None:
                aspects["decimals"] = str(self.decimals)
            elif self.precision is not None:
                aspects["precision"] = str(self.precision)

        if isinstance( self.value, datetime.datetime):
            # Format dates:
            value_literal = self.value.isoformat(sep='T')
        elif isinstance( self.value, bool):
            # booleans are written as boolean literals
            value_literal = self.value
        elif isinstance( self.value, type(None)):
            # So are Nones:
            value_literal = self.value
        else:
            # All else gets converted to string:
            value_literal = str(self.value)
        return { "aspects": aspects,
                 "value": value_literal}


class Concept(object):
    """
    Represents metadata about concepts and their relationships:
    instances of this class are nodes in a tree data structure to keep track
    of which concepts are parents/children of other concepts in the schema hierarchy.
    Also stores concept metadata derived from the schema.
    """
    def __init__(self, taxonomy, concept_name):
        """
        Constructs a Concept instance with no parent and no children.
        Args:
          taxonomy: reference to the global Taxonomy instance
            used to look up information about the named concept.
          concept_name: string
            name of an XBRL Concept in the taxonomy
        Raises:
          Nothing, but prints a warning if concept_name is not found in taxonomy
        """
        self.name = concept_name
        self.parent = None
        self.children = []
        self.validator = validator.Validator(taxonomy)

        try:
            self.metadata = taxonomy.semantic.get_concept_details(concept_name)
        except KeyError as e:
            print("Warning: no metadata found for {}".format(concept_name))
        # FUTURE TODO should we just let this exception go, actually?

    def get_details(self, field_name):
        """
        Args:
          field_name: string
            name of the concept metadata field to be queried.
            Accepted field_names are:
            'period_type'
            'nillable'
            'abstract'
            'id'
            'name'
            'substitution_group'
            'type_name'
            'period_independent'
            'typed_domain_ref' (only present for dimension concepts)
        Returns:
          concept metadata value for the named field, or None if there
          is no value for that field. 
        """
        return getattr( self.metadata, field_name, None)

    def set_parent(self, new_parent):
        """
        Sets the parent concept (in the tree structure) of this concept
        Args:
          new_parent: Concept instance
            new_parent becomes parent of this concept, this concept becomes
            child of parent
        """
        self.parent = new_parent
        if self not in self.parent.children:
            self.parent.children.append(self)

    def add_child(self, new_child):
        """
        Adds a child concept (in the tree structure) to this concept.
        Args:
          new_child: Concept instance
            new_child becomes a child of this concept, this concept becomes
            parent of child
        """
        if new_child not in self.children:
            self.children.append(new_child)
        new_child.parent = self

    def get_ancestors(self):
        """
        Gets all of the concept's ancestors (in the tree structure)
        Returns:
          flat list of Concept instances, including the concept's parent,
          its parent's parent, etc. recursively up to the root of the tree.
        """
        ancestors = []
        curr = self
        while curr.parent is not None:
            ancestors.append(curr.parent)
            curr = curr.parent
        return ancestors

    def validate_datatype(self, value):
        """
        Checks whether the given value is a valid one for this concept, given
        this concept's data type.
        Please note: this method is slated to be moved to the validator module.
        Args:
          value: a float, integer, string, boolean, or date
        Returns:
          True if the given value matches the expected type of this concept.
          e.g. integer, string, decimal, boolean, or complex enumerated type.
          False otherwise.
        """
        return not self.validator.validate_concept_value(self.metadata, value)[1]
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
        # print("Warning: i don't know how to validate " + myType)

        # TODO add validation for complex types.  Most types in the num:
        # namespace will be decimals that expect units. Most types in
        # the solar-types: namespace will be enumerated string types.
        return True


class Axis(Concept):
    """
    A table axis. All Axes are concepts, but not all concepts are Axes, so this
    class is a subclass of Concept. In addition to the fields of a Concept,
    an Axis may also have a Domain and a finite set of allowed Domain Members.
    """
    def __init__(self, taxonomy, concept_name):
        """
        Constructs an Axis instance with no parent and no children.
        Args:
          taxonomy: reference to the global Taxonomy instance
            used to look up information about the named concept.
          concept_name: string
            name of an XBRL Concept in the taxonomy
        Raises:
          Nothing, but prints a warning if concept_name is not found in taxonomy
        """
        super(Axis, self).__init__(taxonomy, concept_name)
        self.domain = None
        self.domainMembers = []

    def get_domain(self):
        """
        Returns:
          the domain of the axis (a string, naming another concept)
        """
        if self.domain is not None:
            return self.domain
        # TODO in what case is domain none but domain_ref not none?
        domain_ref = self.get_details("typed_domain_ref")

        if domain_ref is not None:
            # The typed_domain_ref metadata property will contain something like
            #    "#solar_ProductIdentifierDomain"  which is actually an internal link
            # to an ID inside the taxonomy XML document. I am making the assumption here
            # that it can be easily translated to an actual domain name by just replacing
            # "#solar_" with "solar": but a better approach would be to look up the element
            # matching the ID and read the name from that element.
            # Also dei and us-gaap namespaces follow same patter.
            if "#solar_" in domain_ref:
                return domain_ref.replace("#solar_", "solar:")
            elif "#dei_" in domain_ref:
                return domain_ref.replace("#dei_", "dei:")
            elif "#dei_" in domain_ref:
                return domain_ref.replace("#us-gaap_", "us-gaap:")
        return None




class OBInstance(object):
    """
    Data structure representing an Orange Button Instance document.
    (Apologies if the name is confusing: the name of this thing in XBRL
    nomenclature is an "instance", not to be confused with "an instance
    of a class" in Python.)
    You can think of an XBRL Instance as a kind of abstract document that
    stores Facts in a format-agnostic way. It doesn't become a physical
    document until it's exported as a particular data format.

    Each Fact provides a value for a certain Concept within a certain Context.
    An OBInstance is more than just a list of facts, however -- the facts
    and contexts may be grouped into one or more Hypercubes (tables).

    An OBInstance usually has a single "entrypoint" defining what Concepts
    it can hold. For example, if the entrypoint is "MonthlyOperatingReport",
    that means this instance document represents a monthly operating report,
    and is restricted to storing the Concepts that the Orange Button schema
    allows in a Monthly Operating Report. (There is not always a single
    entrypoint, though -- the spec supports a multiple-entrypoint Instance
    or an Instance with no entrypoint. These are not implemented yet.)
    """
    def __init__(self, entrypoint_name, taxonomy, dev_validation_off=False):
        """
        Constructs an OBInstance instance. It starts out empty, until Facts
        are added.
        Args:
          entrypoint_name: string
            Either the name of an Entrypoint as defined in the Orange Button
            schema -- for example, "CutSheet", "MonthlyOperatingReport", "System"
            -- or the string "All".  If an Entrypoint is named, then this
            OBInstance is restricted to holding only the XBRL Concepts allowed
            by the taxonomy for that Entrypoint. If the string "All" is given,
            then there is no restriction and ANY XBRL Concept from the
            Orange Button taxonomy may be used.
          taxonomy: reference to the Taxonomy singleton.
            reference is stored and used to look up taxonomy relationships.
          dev_validation_off: boolean
            default False. Set it to True to turn validation rules off during 
            development. This should not be used during a release.
        Raises:
          OBNotFoundError if the named Entrypoint cannot be found.
        """
        self.ts = taxonomy.semantic
        self.tu = taxonomy.units
        self.taxonomy = taxonomy
        self.entrypoint_name = entrypoint_name
        self._dev_validation_off = dev_validation_off
        self._all_my_concepts = {}


        if not self.ts.is_entrypoint(entrypoint_name):
            raise OBNotFoundError(
                "There is no Orange Button entrypoint named {}.".format(
                    entrypoint_name))

        # This gives me the list of every concept that could ever be
        # included in the document.
        concept_list = self.ts.get_entrypoint_concepts(entrypoint_name)
        self._initialize_concepts(concept_list)

        # Get the relationships (this comes from solar_taxonomy/documents/
        #  <entrypoint>/<entrypoint><version>_def.xml)
        self.relations = self.ts.get_entrypoint_relationships(entrypoint_name)

        # Search through the relationships to find all of the tables, their
        # axes, and parent/child relationships between concepts:
        self._initialize_parents()
        self._initialize_tables()

        self.facts = {}
        self.taxonomy_name = "https://raw.githubusercontent.com/SunSpecOrangeButton/solar-taxonomy/master/core/solar_all_2019-02-27_r01.xsd"
        self._default_context = {}

    def _initialize_concepts(self, concept_name_list):
        """
        Initializes the internal Concept dictionary of the instance. Called by the
        constructor, client code should not call this.
        Args:
          concept_name_list: list of strings
            names of every concept allowed in this document.
        """
        for concept_name in concept_name_list:
            if concept_name.endswith("_1"):
                # There are a bunch of duplicate concept names that all end in "_1"
                # that raise an exception if we try to query them.
                continue
            # Use substitution group to check whether this concept should be an
            # Axis, and if so, instantiate the Axis subclass:
            subgrp = self.ts.get_concept_details(concept_name).substitution_group
            if subgrp.name == 'dimension':
                new_concept = Axis(self.taxonomy, concept_name)
            else:
                new_concept = Concept(self.taxonomy, concept_name)
            self._all_my_concepts[concept_name] = new_concept

    def _initialize_tables(self):
        """
        Initializes the internal Hypercube (table) structures of the OBInstance,
        using relations from the taxonomy to find the axes and lineitems for each one.
        Called by the constructor, client code should NOT call this.
        Args: None
        Returns: None
        """
        # When there's an arcrole of "hypercube-dimensions", the "from"
        # is a hypercube/table, and the "to" is an axis. Use these
        # relationships to find all hypercube names.
        self._tables = {}
        all_table_names = set([])
        for relation in self.relations:
            if relation.role == taxonomy.RelationshipRole.hypercube_dimension:
                table_name = relation.from_
                all_table_names.add(table_name)

        for table_name in all_table_names:
            self._tables[table_name] = Hypercube(self, table_name)

    def _initialize_parents(self):
        """
        Initializes the internal Concept tree of the Instance, using relations
        from the taxonomy to relate parents to children in a tree structure.
        Called by the constructor, client code should NOT call this.
        Args: None
        Returns: None
        """
        for relation in self.relations:
            if relation.role == taxonomy.RelationshipRole.domain_member:
                parent_name = relation.from_
                child_name = relation.to
                if parent_name.endswith("_1") or child_name.endswith("_1"):
                    # These are the duplicate concept names and are unwanted
                    continue
                parent = self.get_concept(parent_name)
                child = self.get_concept(child_name)
                parent.add_child(child)

    def _get_namespaces(self):
        """
        Gets all namespaces that need to be included in the header of this
        document.
        Args: None
        Returns: dictionary where keys are "xmlns:<namespace>" definitions and
            values are URLs.
        """
        # The following namespaces are basic and are always included.
        namespaces = {
            "xmlns": "http://www.xbrl.org/2003/instance",
            "xmlns:link": "http://www.xbrl.org/2003/linkbase",
            "xmlns:xlink": "http://www.w3.org/1999/xlink",
            "xmlns:xsi": "http://www.w3.org/2001/XMRLSchema-instance",
            "xmlns:units": "http://www.xbrl.org/2009/utr",
            "xmlns:xbrldi": "http://xbrl.org/2006/xbrldi",
            "xmlns:solar": "http://xbrl.us/Solar/v1.3/2019-02-27/solar"
        }

        # The following namespaces are optional and are included in the header
        # only if they are referred to by a fact in this instance document.
        optional_namespaces = {
            "us-gaap": "http://xbrl.fasb.org/us-gaap/2017/elts/us-gaap-2017-01-31.xsd"
        }
        for fact in self.get_all_facts():
            concept_prefix = fact.concept_name.split(":")[0]
            for ns in optional_namespaces:
                if concept_prefix == ns:
                    namespaces[ "xmlns:{}".format(ns)] = optional_namespaces[ns]

        return namespaces

    def get_concept(self, concept_name):
        """
        Args:
          concept_name: string
            name of a concept 
        Returns:
          Concept instance matching concept_name, if it's a concept allowed
          in this instance document by the entrypoint.
        """
        return self._all_my_concepts[concept_name]

    def get_table_names(self):
        """
        Args: None
        Returns:
          A list of strings identifying all table (hypercubes) allowed
          in this instance document by the entrypoint.
        """
        return list(self._tables.keys())

    def get_table(self, table_name):
        """
        Args:
          table_name: string
            name of a table (Hypercube)
        Returns:
          Hypercube instance matching the given table_name string, if it's a
          table allowed in this instance document by the entrypoint.
        """
        return self._tables[table_name]

    def _identify_relations(self, concept_name):
        """
        Development method that lists all relationships for the given concept,
        for debugging purposes. Do not use in production.
        Args:
          concept_name: string
            name of a concept
        Returns: None
        """
        from_me = [r for r in self.relations if r['from'] == concept_name]
        for x in from_me:
            print("{} -> {} -> {}".format(concept_name, x.role, x.to))
        to_me = [r for r in self.relations if r.to == concept_name]
        for x in to_me:
            print("{} -> {} -> {}".format(x.from_, x.role, concept_name))

    def get_table_for_concept(self, concept_name):
        """
        Args:
          concept_name: string
            name of a concept that can be written to this instance document
        Returns:
          Hypercube instance -- the table where the named concept belongs,
          if the named concept belongs on a table in this instance document.
          Note there are some concepts that belong in the instance document
          but not in any table. In that case, returns a placeholder table
          identified by the constant UNTABLE.
        """
        if concept_name not in self._all_my_concepts:
            raise OBConceptError(
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
        Returns:
          list of strings. Strings are the names of all concepts that can be written
          to this instance document as allowed by the entrypoint.
        """
        return [c for c in self._all_my_concepts if self.is_concept_writable(c)]

    def is_concept_writable(self, concept_name):
        """
        Args:
          concept_name: string
            name of a concept
        Returns:
          True if concept_name is a writeable concept within this
          document. False for concepts not in this document or concepts that
          are only abstract parents of writeable concepts. e.g. you can't
          write a value to an "Abstract" or a "LineItem".
        """
        if concept_name in self._all_my_concepts:
            concept = self._all_my_concepts[concept_name]
            abstract = concept.get_details("abstract")
            if abstract:
                return False
            return True
        return False

    def _is_valid_context(self, concept_name, context):
        """
        Args:
          concept_name: string
            name of a concept that can be written to this instance document
          context: Context instance
            context to validate.
        Returns:
          True if the given Context object contains all the information
          needed to provide full context for the named concept. i.e. if it
          provides either a valid duration or a valid instant, whichever
          the concept requires, and it also provides valid values for each and
          every dimension (Axis) required by the table where the concept resides.
        Raises:
          OBContextError explaining what is wrong, if some needed information
          is missing or invalid.
        """
        if not isinstance(context, Context):
            raise OBContextError("{} is not a valid Context instance".format(context))

        # TODO Refactor to put this logic into the Concept?
        period_type = self.get_concept(concept_name).get_details("period_type")

        if taxonomy.PeriodType(period_type) == taxonomy.PeriodType.duration:
            if not context.duration:
                raise OBContextError(
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
                raise OBContextError(
                    "Invalid duration in {} context".format(
                        concept_name))

        if taxonomy.PeriodType(period_type) == taxonomy.PeriodType.instant:
            if not context.instant:
                raise OBContextError(
                    "Missing required instant in {} context".format(
                        concept_name))
                # TODO check isinstance(instant, datetime)

        # If we got this far, we know the time period is OK. Now check the
        # required axes, if this concept is on a table:
        table = self.get_table_for_concept(concept_name)
        if table is not None:
            table._is_valid_context(context)

        return True

    def _is_valid_unit(self, concept_name, unit_id):
        """
        Args:
          concept_name: string
            name of a concept that can be written to this instance document
          unit_id: string
            id of a unit that can be
        Returns:
          True if the unit can be used to write a value to the named concept.
          For example, if a concept is a measurement of energy, then kWh
          is a valid unit but kW is not.
        Raises:
          OBUnitError explaining why the unit is not valid.
        """
        # TODO Refactor to move this logic into the Concept class or place in Parser?
        # TODO Examine full definition of valid units and update logic to be completely equitable

        unitlessTypes = ["xbrli:integerItemType", "xbrli:stringItemType",
                         "xbrli:decimalItemType", "xbrli:booleanItemType",
                         "xbrli:dateItemType", "num:percentItemType",
                         "xbrli:anyURIItemType", "dei:legalEntityIdentifierItemType"]
        # NOTE: As a quick fix dei:legalEntityIdentifier Type has been added so that the sample programs
        # works but this is a case of using hardcoding as opposed to correct logic.

        # There is type-checking we can do for these unitless types but we'll handle
        # it elsewhere
        
        required_type = self.get_concept(concept_name).get_details("type_name")
        if required_type in unitlessTypes:
            if unit_id is None:
                return True
            else:
                raise OBUnitError(
                    "Unit {} given for unitless concept {} ({})".format(
                        unit_id, concept_name, required_type))

        if required_type.startswith("solar-types:"):
            # print("I don't know how to validate {} yet, skipping for now".format(required_type))
            return True

        # TODO what other required_types might we get here?

        if unit_id is None:
            raise OBUnitError(
                "No unit given for concept {}, requires type {}".format(
                    concept_name, required_type))

        unit = self.tu.get_unit(unit_id)
        if not unit:
            raise OBNotFoundError(
                "There is no unit with unit_id={} in the taxonomy."
                 .format(unit_id))

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
        Adds a fact to the document. Stores a Fact that sets the named
        concept to the given value within the given context.
        
        If concept_name and context are identical to a previous call, the old fact
        will be overwritten. Otherwise, a new fact is created.

        The context can be provided in one of two ways: either a Context object
        passed in using the 'context=' keyword arg, OR the duration/instant, entity,
        and extra axes that define a context can all be passed in as separate keyword
        args. (Not both!)

        Args:
          concept_name: string
            name of a concept that can be written to this instance document
          value: string, float, int, boolean, or date
            value to set for the concept
        Keyword Args:
          context: a Context instance
            context for the fact being set. Required unless supplying duration/instant
            entity/axes separately.
          unit_name: string
            required if value is a numeric type. Specifies the unit in which the value
            is counted.
          precision: integer
            number of significant digits of precision (for decimal values only)
          decimals: integer
            number of places past the decimal point to be considered precise. (For
            decimal values only. Only one of precision or decimals is accepted, not
            both. Defaults to decimals=2.)
          fact_id: string
            Optional ID for a fact.  If not passed in it is auto-generated.
          instant: datetime
            instant value for the context, if "context" is not given
          duration: a dict with start and end fields {"start": <date>, "end": <date>}
            duration value for the context, if "context" is not given
          entity: string
            entity value for the context, if "context" is not given
          <axis name (*Axis)>: <axis value>
            as a convenience, instant/duration, entity, and <axis name> can be given
            directly as keyword args instead of constructing and passing a Context
            argument. These should only be passed in if the "context" keyword arg
            is not used.  See the Context class constructor for more details -- usage
            is identical.
          
        Returns:
          None
        Raises:
          OBConceptError: if the concept is not writable in this document
          OBContextError: if the context is not correct for the concept
          OBUnitError: if the unit given is wrong for the concept
          OBTypeError: if the value given is the wrong type for the concept
        """

        if "unit_name" in kwargs:
            unit_name = kwargs.pop("unit_name")
            valid_unit_name = self.tu.is_unit(unit_name)
        else:
            unit_name = None
            valid_unit_name = False

        if "precision" in kwargs:
            precision = kwargs.pop("precision")
        else:
            precision = None

        if "decimals" in kwargs:
            decimals = kwargs.pop("decimals")
        else:
            decimals = None

        if "fact_id" in kwargs:
            fact_id = kwargs.pop("fact_id")
        else:
            fact_id = None

        if not self.is_concept_writable(concept_name):
            raise OBConceptError(
                "{} is not a writeable concept".format(concept_name))
        concept = self.get_concept(concept_name)

        if "context" in kwargs:
            context = kwargs.pop("context")
        elif len(list(kwargs.keys())) > 0:
            # turn the remaining keyword args into a Context object -- this
            # is just syntactic sugar to make this method easier to call.
            # TODO this block will not work
            period = concept.get_details("period_type")
            if period not in kwargs and period in self._default_context:
                kwargs[period.value] = self._default_context[period]
            context = Context(**kwargs)
        else:
            context = None

        # Use default values, if any have been set, to fill in missing fields of context:
        if len(self._default_context) > 0:
            context = self._fill_in_context_from_defaults(context, concept)

        if not self._is_valid_context(concept_name, context):
            raise OBContextError(
                "Insufficient context for {}".format(concept_name))

        # Check unit type:
        if not self._dev_validation_off and not  self._is_valid_unit(concept_name, unit_name):
            raise OBUnitError(
                "{} is not a valid unit name for {}".format(unit_name, concept_name))

        # check datatype of given value against concept
        if not self._dev_validation_off and not concept.validate_datatype(value):
            raise OBTypeError(
                "{} is the wrong datatype for {}".format(value, concept_name))

        table = self.get_table_for_concept(concept_name)
        context = table.store_context(context) # dedupes, assigns ID

        f = Fact(concept_name, context, unit_name, value,
                 precision=precision,
                 decimals=decimals,
                 id=fact_id)

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

    def get(self, concept_name, context=None):
        """
        Looks up the value of a fact given its concept name and context.
        Args:
          concept_name: string
            Name of the concept to get the value for.
          context: Context instance
            The context identifying the fact to look up.
        Returns:
          The value of the fact previously set, if a match is found for
          concept_name and context. None if no match is found.
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
        table = self.get_table_for_concept(concept_name)
        context = table.lookup_context(context)
        if table.get_name() in self.facts:
            if context.get_id() in self.facts[table.get_name()]:
                if concept_name in self.facts[table.get_name()][context.get_id()]:
                    return self.facts[table.get_name()][context.get_id()][concept_name]
        return None

    def get_all_facts(self):
        """
        Returns: 
            a list of Fact. All facts are returned in a single list, regardless
            of which table or context they belong to.
        """
        all_facts = []
        for table_dict in list(self.facts.values()):
            for context_dict in list(table_dict.values()):
                for fact in list(context_dict.values()):
                    all_facts.append(fact)
        return all_facts

    def _make_unit_tag(self, unit_id):
        """
        Args:
          unit_id: string
            ID of any unit in the taxonomy
        Returns:
          an XML Element representing the unit, to be included in the
          XML-format XBRL document.
        """
        # TODO validate that this unit_id is valid and matches something
        # in the taxonomy.
        # See http://www.xbrl.org/utr/utr.xml
        unit = Element("unit", attrib={"id": unit_id})
        measure = SubElement(unit, "measure")
        measure.text = "units:{}".format(unit_id)
        # because http://www.xbrl.org/2009/utr is included as xmlns:units

        return unit

    def _toXML_tag(self):
        """
        Returns:
          an XML Element which is the root of an XML tree representing
          the entire document contents (all contexts, units, and facts) in 
          XML-format XBRL.
        """
        # The root element:
        xbrl = Element("xbrl", attrib = self._get_namespaces())

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
        Exports the document as XML-formatted XBRL to the given filename
        Note: this method is slated to be moved to Parser.
        To ensure future support use the method with the same name and
        functionality in Parser.

        Args:
          filename: string
            filesystem path of a location to write the document to.
        """
        xbrl = self._toXML_tag()

        # Apparently every XML file should start with this, which ElementTree
        # doesn't do:
        # <?xml version="1.0" encoding="utf-8"?>
        tree = xml.etree.ElementTree.ElementTree(xbrl)
        tree.write(filename)

    def to_XML_string(self):
        """
        Exports the document as XML-formatted XBRL string
        Note: this method is slated to be moved to Parser.
        To ensure future support use the method with the same name and
        functionality in Parser.

        Returns:
          String containing entire document as XML-formatted XBRL.
        """
        xbrl = self._toXML_tag()
        return xml.etree.ElementTree.tostring(xbrl).decode()

    def to_JSON(self, filename):
        """
        Exports the document as JSON-formatted XBRL to the given filename
        Note: this method is slated to be moved to Parser.
        To ensure future support use the method with the same name and
        functionality in Parser.

        Args:
          filename: string
            filesystem path of a location to write the document to.
        """
        outfile = open(filename, "w")
        outfile.write(self.to_JSON_string())
        outfile.close()

    def to_JSON_string(self):
        """
        Exports the document as JSON-formatted XBRL string
        Note: this method is slated to be moved to Parser.
        To ensure future support use the method with the same name and
        functionality in Parser.

        Returns:
          String containing entire document as JSON-formatted XBRL.
        """
        masterJsonObj = {
            "documentType": "http://www.xbrl.org/WGWD/YYYY-MM-DD/xbrl-json",
            "prefixes": self._get_namespaces(),
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
        Set default values for context entity, instant/duration, and/or axes.
        The default values are used to fill in any fields that are missing
        from any contexts passed into set().

        For example:
          document.set_default_context({"entity": "MyCompanyName"})
        sets "MyCompanyName" as the default "entity" of this document. From
        then on, you can call document.set() without providing an entity in
        the context, and "MyCompanyName" will be used as the entity.
        You can set a default for an axis and it will simply be ignored by any
        contexts that do not require that axis.

        Args:
          dictionary: a python dict that can have the following keys:
            "entity": string, entity name to set as default for all contexts.
            PeriodType.instant: date to set as default for all instant-period
              contexts.
            PeriodType.duration: either a dict with keys "start" and "end"
              whose values are dates, OR the literal string "forever". This
              will be set as default for all duration-period contexts.
            <*Axis>: If the key is the name of an Axis on one of the document's
              tables, and the value is a valid value for that axis, then the
              value will be used as default value for that axis for all
              contexts that require it.
        """
        self._default_context.update(dictionary)

    def _fill_in_context_from_defaults(self, context, concept):
        """
        Uses default values (set by using set_default_context()) to fill in any
        missing fields in a given context object.

        Args:
          context: a Context instance, or None.
            if provided, values are used to override the defaults
          concept: a Concept object
            concept that a context is intended to be used with. The concept is
            used to determine what fields are required in the context.

        Returns: a new Context object. The returned Context has field values
          (entity, duration/instant, axes) copied from the context argument where
          available and filled in from the default context
          (see set_default_context()) for any fields not present in the context
          argument. If context argument was None, then all field values will be
          taken from the defaults.
        """
        period = concept.get_details("period_type") # PeriodType.instant or PeriodType.duration
        if context is None:
            # Create context from default entity and default period:
            context_args = {}
            if period in self._default_context:
                context_args[period.value] = self._default_context[period]
            else:
                raise OBContextError(
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

        Returns: true if all of the facts in the document validate.
          i.e. they have allowed data types, allowed units, anything that needs
          to be in a table has all the required axis values to identify its place
          in that table, etc.
        """
        return True

    def is_complete(self):
        """
        (Placeholder).

        Returns: True if no required facts are missing, i.e. if
          there is a value for all concepts with nillable=False
        """
        return True
