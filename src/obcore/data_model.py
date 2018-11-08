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

from taxonomy_semantic import TaxonomySemantic


class Hypercube(object):
    """
    (Currently a placeholder) a data structure to represent a table
    (aka a Hypercube) within a document.
    """
    def __init__(self, table_name, axis_names):
        self._table_name = table_name
        self._axis_names = axis_names

    def name(self):
        return self._table_name

    def axes(self):
        return self._axis_names


class Entrypoint(object):
    """
    A data structure representing an orange button document
    from a particular entrypoint -- for example, an MOR.
    This class's representation of the data is format-agnostic, it just
    provides methods for getting/setting and validation; translation to
    and from particular physical file format (or database schema) will
    be handled elsewhere.
    """
    def __init__(self, entrypoint_name):
        """
        Initializes an empty instance of a document corresponding to the named
        entrypoint. entrypoint_name is a string that must match an entry point in
        the taxonomy. Looks up the list of concepts for this entry point from
        the taxonomy to know what concepts are allowed in the document.
        Looks up the relationships between concepts for this entry point from
        the taxonomy to know the hierarchical relationship of concepts, tables,
        and axes/dimensions.
        """
        self.ts = TaxonomySemantic()

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
        # Search through the relationships to find all of the tables and
        # their axes:
        self._find_tables()


    def allowedConcepts(self):
        return self._all_allowed_concepts

    def _find_tables(self):
        """
        Uses relations to find all of the tables (hypercubes) allowed in
        the document, and the axes for each one.
        """
        # When there's an arcrole of "hypercube-dimensions", the "from"
        # is a hypercube/table, and the "to" is an axis.
        self._tables = []
        axes = {}
        for relation in self.relations:
            if relation['role'] == 'hypercube-dimension':
                table_name = relation['from']
                axis_name = relation['to']
                if not table_name in axes:
                    axes[table_name] = []
                axes[table_name].append(axis_name)
        for table_name in axes:
            self._tables.append( Hypercube( table_name, axes[table_name] ))

    def getTables(self):
        return self._tables

    def _identify_relations(self, concept_name):
        # Development method for listing all relationships for debugging
        # purposes. Do not use in production.
        from_me = [r for r in self.relations if r['from'] == concept_name]
        for x in from_me:
            print "{} -> {} -> {}".format(concept_name, x['role'], x['to'])
        to_me = [r for r in self.relations if r['to'] == concept_name]
        for x in to_me:
            print "{} -> {} -> {}".format(x['from'], x['role'], concept_name)


    def set(self, concept, value, context=None):
        """
        (Placeholder) Adds a fact to the document. The concept and the context
        together identify the fact to set, and the value will be stored for
        that fact.
        If concept and context are identical to a previous call, the old fact
        will be overwritten. Otherwise, a new fact is created.
        """
        # If context is None, use a default context. (A few concepts
        # won't need any other context information beyond this.)
        # complain if value is invalid for concept
        # complain if context is needed and not present
        # complain if context has wrong unit
        # complain if context has wrong duration/instant type
        # add to facts

        # We can look up a concept name like this:
        # x = self.ts.concept_info('solar:BatteryRating')
        # this gives me properties like:
        #x.period_type
        #x.nillable
        #x.id
        #x.name
        #x.substitution_group
        #x.type_name
        #x.period_independent
        # Which will be useful for validation.

        pass

    def get(self, concept, context=None):
        """
        (Placeholder) Returns the value of a fact previously set. The concept
        and context together identify the fact to read.
        """
        # look up the facts we have
        # (context not needed if we only have one fact for this concept)
        # complain if no value for concept
        # complain if context needed and not provided
        #
        pass

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

