"""Orange Button data model."""

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import taxonomy


class Hypercube(object):
    """
    Hypercube placeholder.

    (Currently a placeholder) a data structure to represent a table
    (aka a Hypercube) within a document.
    """

    def __init__(self, table_name, axis_names):
        """Hypercube cnstructor."""
        self._table_name = table_name
        self._axis_names = axis_names
        self._line_items = []

    def name(self):
        """Return table name."""
        return self._table_name

    def axes(self):
        """Return axes names."""
        return self._axis_names

    def addLineItem(self, line_item_name):
        """Add a line item."""
        self._line_items = line_item_name

    def hasLineItem(self, line_item_name):
        """Check if hypercube contains a line item."""
        return line_item_name in self._line_items


class Context(object):
    """Handles data model context."""

    def __init__(self, **kwargs):
        """Context constructor."""
        # kwargs must provide exactly one of instant or duration
        if "instant" in kwargs and "duration" in kwargs:
            raise Exception("Context given both instant and duration")
        if ("instant" not in kwargs) and ("duration" not in kwargs):
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


class Concept(object):
    """Handles Orange Button concepts."""

    def __init__(self, concept_name):
        """Concept constructor."""
        self.name = concept_name
        self.parent = None
        self.children = []

    def setParent(self, new_parent):
        """Set a concept parent."""
        self.parent = new_parent
        if self not in self.parent.children:
            self.parent.children.append(self)

    def addChild(self, new_child):
        """Add a child concept."""
        if new_child not in self.children:
            self.children.append(new_child)
        new_child.parent = self

    def getAncestors(self):
        """Return a concepts parent and other ancestors."""
        ancestors = []
        curr = self
        while curr.parent is not None:
            ancestors.append(curr.parent)
            curr = curr.parent
        return ancestors


class Entrypoint(object):
    """
    Data structure representing an entrypoint.

    A data structure representing an orange button document
    from a particular entrypoint -- for example, an MOR.
    This class's representation of the data is format-agnostic, it just
    provides methods for getting/setting and validation; translation to
    and from particular physical file format (or database schema) will
    be handled elsewhere.
    """

    def __init__(self, entrypoint_name, taxonomy):
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
        """
        self.ts = taxonomy.semantic
        self.tu = taxonomy.units
        self.entrypoint_name = entrypoint_name
        if not self.ts.validate_ep(entrypoint_name):
            raise Exception("There is no Orange Button entrypoint named {}.".format(entrypoint_name))

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

    def allowedConcepts(self):
        """Return all allowed concepts."""
        return self._all_allowed_concepts

    def _find_tables(self):
        """
        Find tables.

        Use relations to find all of the tables (hypercubes) allowed in
        the document, and the axes and lineitems for each one.
        """
        # When there's an arcrole of "hypercube-dimensions", the "from"
        # is a hypercube/table, and the "to" is an axis.

        self._tables = {}
        axes = {}
        for relation in self.relations:
            if relation['role'] == 'hypercube-dimension':
                table_name = relation['from']
                axis_name = relation['to']
                if table_name not in axes:
                    axes[table_name] = []
                axes[table_name].append(axis_name)
        for table_name in axes:
            self._tables[table_name] = Hypercube(table_name, axes[table_name])

        # If there's an arcrole of "all" then the "from" is a LineItems
        # and the "to" is the table?  I think?
        for relation in self.relations:
            if relation['role'] == 'all':
                line_item = relation['from']
                table_name = relation['to']
                table = self._tables[table_name]
                table.addLineItem(line_item)

    def _find_parents(self):
        """Put the concepts into a tree based on domain-member relations."""
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
        """Return table names."""
        return self._tables.keys()

    def getTable(self, table_name):
        """Return a given table."""
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

    def getTableForConcept(self, concept_name):
        """
        Returns the table for a concept.

        Given a concept_name, returns the table (Hypercube object) which
        that concept belongs inside of, or None if there's no match.
        """
        if concept_name not in self._all_allowed_concepts:
            raise Exception("{} is not an allowed concept for {}".format(
                concept_name, self.entrypoint_name))

        # We know that a concept belongs in a table because the concept
        # is a descendant of a LineItem that has a relationship to the
        # table.
        if concept_name not in self.all_my_concepts:
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
        Return whether a concept is writable.

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
        Return whether a context object has sufficient information.

        True if the given Context object contains all the information
        needed to provide full context for the named concept -- sufficient
        time period information (duration/instant), sufficient axes to place
        the fact within its table, etc.
        Otherwise, raises an exception explaining what is wrong.
        """
        # Refactor to put this logic into the Concept?
        # make the Context into an object instead of a dictionary?
        # do Context arguments as **kwargs ?

        metadata = self.ts.concept_info(concept_name)
        if metadata.period_type == taxonomy.PeriodType.duration:
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


        if metadata.period_type == taxonomy.PeriodType.instant:
            if not context.instant:
                raise Exception("Missing required instant in {} context".format(
                    concept_name))
                # TODO check isinstance(instant, datetime)

        # If we got this far, we know the time period is OK. Now check the
        # required axes, if this concept is on a table:
        table = self.getTableForConcept(concept_name)
        if table is not None:
            for axis in table.axes():
                if axis not in context.axes:
                    raise Exception("Missing required {} axis for {}".format(
                        axis, concept_name))
                # Check that the value given of context.axes[axis] is valid!
                # (How do we do that?)
        # TODO check that we haven't given any EXTRA axes that the table
        # DOESN'T want?

        return True

    def set(self, concept, value, **kwargs):
        """
        Fact placeholder.

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
        if "unit_name" in kwargs:
            unit_name = kwargs.pop("unit_name")
            valid_unit_name = self.tu.validate_unit(unit_name=unit_name)
        if "precision" in kwargs:
            precision = kwargs.pop("precision")

        if concept not in self._all_allowed_concepts:
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
            raise Exception("Insufficient context for {}".format(concept))

        concept_ancestors = self.all_my_concepts[concept].getAncestors()
        concept_metadata = self.ts.concept_info(concept)
        table = self.getTableForConcept(concept)

        # complain if value is invalid for concept
        # complain if context is needed and not present
        # complain if context has wrong unit
        # complain if context has wrong duration/instant type
        # add to facts

        # figure out the data structure for facts that can be keyed on
        # context as well as concept.  Probably need to copy over the logic
        # from py-xbrl-generator that turns context values into a context ID.
        self.facts[concept] = value

        # concept_metadata properties:
        # x.period_type
        # x.nillable
        # x.id
        # x.name
        # x.substitution_group
        # x.type_name
        # x.period_independent
        # Which will be useful for validation.

    def get(self, concept, context=None):
        """
        (Placeholder) Returns the value of a fact previously set.

        The concept and context together identify the fact to read.
        """
        # look up the facts we have
        # (context not needed if we only have one fact for this concept)
        # complain if no value for concept
        # complain if context needed and not provided
        #
        return self.facts[concept]

    def isValid(self):
        """
        (Placeholder).

        Returns true if all of the facts in the document validate.
        i.e. they have allowed data types, allowed units, anything that needs
        to be in a table has all the required axis values to identify its place
        in that table, etc.
        """
        return True

    def isComplete(self):
        """
        (Placeholder).

        (Placeholder) Returns true if no required facts are missing, i.e. if
        there is a value for all concepts with nillable=False
        """
        return True
