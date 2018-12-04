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

import unittest
from data_model import Entrypoint, Context, Hypercube
from datetime import datetime
from taxonomy import getTaxonomy
from lxml import etree
import json

class TestDataModelEntrypoint(unittest.TestCase):

    def setUp(self):
        self.taxonomy = getTaxonomy()

    def tearDown(self):
        pass

    def _check_arrays_equivalent(self, array1, array2):
        # An ugly hack to make the tests work in both python2
        # and python3:
        if hasattr( self, 'assertCountEqual'):
            self.assertCountEqual(array1, array2)
        else:
            self.assertItemsEqual(array1, array2)

        # assertCountEqual is the new name for what was previously
        # assertItemsEqual. assertItemsEqual is unsupported in Python 3
        # but assertCountEqual is unsupported in Python 2.


    def test_instantiate_empty_entrypoint(self):
        doc = Entrypoint("CutSheet", self.taxonomy)

        # The newly initialized CutSheet should have a correct list of
        # allowable concepts as defined by the taxonomy for CutSheets:
        concepts = doc.allowedConcepts()
        # TypeOfDevice is allowed in CutSheets:
        self.assertIn('solar:TypeOfDevice', concepts)
        # AppraisalCounterparties is not allowed in CutSheets:
        self.assertNotIn('solar:AppraisalCounterparties', concepts)

        # The newly initialized CutSheet should have a correct list of tables
        # and each table should have a correct list of axes, as defined by
        # the taxonomy for CutSheets:
        tables = doc.getTableNames()
        self._check_arrays_equivalent(tables,
                                      ["solar:InverterPowerLevelTable",
                                       "solar:CutSheetDetailsTable"])
        self._check_arrays_equivalent(
            doc.getTable("solar:InverterPowerLevelTable").axes(),
                         ["solar:ProductIdentifierAxis",
                          "solar:InverterPowerLevelPercentAxis"])
        self._check_arrays_equivalent(
            doc.getTable("solar:CutSheetDetailsTable").axes(),
                         ["solar:ProductIdentifierAxis",
                          "solar:TestConditionAxis"])

    def test_get_table_for_concept(self):
        doc = Entrypoint("CutSheet", self.taxonomy)
        # The CutSheet instance should know that RevenueMeterFrequency
        # is a concept that belongs in the CutSheetDetailsTable
        table = doc.getTableForConcept("solar:RevenueMeterFrequency")
        self.assertEqual(table.name(), "solar:CutSheetDetailsTable")

        table = doc.getTableForConcept("solar:InverterEfficiencyAtVmaxPercent")
        self.assertEqual(table.name(), "solar:InverterPowerLevelTable")

        # but if we ask for something that is not a line item concept,
        # getTableForConcept should return None:
        table = doc.getTableForConcept("solar:CutSheetDetailsTable")
        self.assertIsNone(table)


    def test_can_write_concept(self):
        doc = Entrypoint("CutSheet", self.taxonomy)

        # Not every concept is writable. For instance, we shouldn't be able
        # to write a value for an Abstract concept, a LineItem group, an Axis,
        # a Domain, etc. even though those are part of this entrypoint.
        self.assertFalse( doc.canWriteConcept('solar:ProductIdentifierModuleAbstract'))
        self.assertTrue( doc.canWriteConcept('solar:TypeOfDevice'))
        self.assertFalse( doc.canWriteConcept('solar:CutSheetDetailsLineItems'))

        self.assertFalse( doc.canWriteConcept('solar:CutSheetDetailsTable'))
        self.assertFalse( doc.canWriteConcept('solar:TestConditionDomain'))

        self.assertFalse( doc.canWriteConcept('solar:ProductIdentifierAxis'))
        self.assertTrue( doc.canWriteConcept('solar:ProductIdentifier'))

    def test_sufficient_context_instant_vs_duration(self):
        doc = Entrypoint("CutSheet", self.taxonomy)

        # in order to set a concept value, sufficient context must be
        # provided. what is sufficient context varies by concept.
        # in general the context must provide the correct time information
        # (either duration or instant)

        # We shouldn't even be able to instantiate a context with no time info:
        with self.assertRaises(Exception):
            noTimeContext = Context(ProductIdentifierAxis = "placeholder",
                                    TestConditionAxis= "placeholder")

        # solar:DeviceCost has period_type instant
        # so it requires a context with an instant. A context without an instant
        # should be insufficient:
        instantContext = Context(ProductIdentifierAxis = "placeholder",
                                 TestConditionAxis = "placeholder",
                                 instant = datetime.now())
        durationContext = Context(ProductIdentifierAxis = "placeholder",
                           TestConditionAxis = "placeholder",
                           duration = "forever")

        self.assertTrue( doc.sufficientContext("solar:DeviceCost",
                                                instantContext))
        # A context with a duration instead of an instant should also be
        # rejected:
        with self.assertRaises(Exception):
            doc.sufficientContext("solar:DeviceCost", durationContext)

        # solar:ModuleNameplateCapacity has period_type duration.
        # A context with an instant instead of a duration should also be
        # rejected:
        with self.assertRaises(Exception):
            doc.sufficientContext("solar:ModuleNameplateCapacity", instantContext)
        self.assertTrue( doc.sufficientContext("solar:ModuleNameplateCapacity",
                                               durationContext))


    def test_sufficient_context_axes(self):
        doc = Entrypoint("CutSheet", self.taxonomy)

        # The context must also provide all of the axes needed to place the
        # fact within the right table.

        # DeviceCost is on the CutSheetDetailsTable so it needs a value
        # for ProductIdentifierAxis and TestConditionAxis.
        with self.assertRaises(Exception):
            doc.sufficientContext("solar:DeviceCost", {})

        context = Context(instant = datetime.now(),
                          ProductIdentifierAxis = "placeholder",
                          TestConditionAxis = "placeholder")
        self.assertTrue( doc.sufficientContext("solar:DeviceCost", context) )

        badContext = Context(instant = datetime.now(),
                             TestConditionAxis = "placeholder")
        with self.assertRaises(Exception):
            doc.sufficientContext("solar:DeviceCost", badContext)

        badContext = Context(instant = datetime.now(),
                             ProductIdentifierAxis = "placeholder")
        with self.assertRaises(Exception):
            doc.sufficientContext("solar:DeviceCost", badContext)


        # How do we know what are valid values for ProductIdentifierAxis and
        # TestConditionAxis?  (I think they are meant to be UUIDs.)

        # Note: TestConditionAxis is part of the following relationships:
        # solar:TestConditionAxis -> dimension-domain -> solar:TestConditionDomain
        # solar:TestConditionAxis -> dimension-default -> solar:TestConditionDomain
        # i wonder what that "dimension-default" means

        #'solar:InverterOutputRatedPowerAC' is on the 'solar:InverterPowerLevelTable' which requires axes: [u'solar:ProductIdentifierAxis', u'solar:InverterPowerLevelPercentAxis']. it's a duration.
        concept = 'solar:InverterOutputRatedPowerAC'
        context = Context(duration = "forever",
                          ProductIdentifierAxis = "placeholder",
                          InverterPowerLevelPercentAxis = "placeholder")
        self.assertTrue( doc.sufficientContext(concept, context))

        badContext = Context(instant = datetime.now(),
                             InverterPowerLevelPercentAxis = "placeholder")
        with self.assertRaises(Exception):
            doc.sufficientContext(concept, badContext)

        badContext = Context(instant = datetime.now(),
                             ProductIdentifierAxis = "placeholder")
        with self.assertRaises(Exception):
            doc.sufficientContext(concept, badContext)


    def test_set_separate_dimension_args(self):
        # Tests the case where .set() is called correctly.  Use the
        # way of calling .set() where we pass in every dimension
        # separately. Verify the data is stored and can be retrieved
        # using .get().
        doc = Entrypoint("CutSheet", self.taxonomy)

        # Write a TypeOfDevice and a DeviceCost:

        doc.set("solar:TypeOfDevice", "Module",
                duration="forever",
                ProductIdentifierAxis= "placeholder",
                TestConditionAxis = "placeholder",
                )
        now = datetime.now()
        doc.set("solar:DeviceCost", 100,
                instant= now,
                ProductIdentifierAxis= "placeholder",
                TestConditionAxis= "placeholder",
                unit="dollars")

        typeFact = doc.get("solar:TypeOfDevice",
                        Context(duration="forever",
                                ProductIdentifierAxis= "placeholder",
                                TestConditionAxis = "placeholder"))
        self.assertEqual( typeFact.value,  "Module")
        costFact = doc.get("solar:DeviceCost",
                           Context(instant = now,
                                ProductIdentifierAxis= "placeholder",
                                TestConditionAxis = "placeholder"))
        self.assertEqual( costFact.value, 100)
        # TODO: DeviceCost should require units

    def test_set_context_arg(self):
        # Tests the case where .set() is called correctly, using
        # the way of calling .set() where we pass in a Context
        # object. Verify the data is stored and can be retrieved
        # using .get().
        doc = Entrypoint("CutSheet", self.taxonomy)
        ctx = Context(duration="forever",
                      entity="JUPITER",
                      ProductIdentifierAxis= "placeholder",
                      TestConditionAxis = "placeholder")
        doc.set("solar:TypeOfDevice", "Module", context=ctx)

        ctx = Context(instant= datetime.now(),
                      entity="JUPITER",
                      ProductIdentifierAxis= "placeholder",
                      TestConditionAxis = "placeholder")
        doc.set("solar:DeviceCost", 100, context=ctx, unit="dollars")


    def test_set_raises_exception(self):
        # Tests the case where .set() is called incorrectly. It should
        # raise exceptions if required information is missing.
        doc = Entrypoint("CutSheet", self.taxonomy)
        with self.assertRaises(Exception):
            doc.set("solar:TypeOfDevice", "Module", {})

        with self.assertRaises(Exception):
            doc.set("solar:DeviceCost", 100, {})

    def test_hypercube_store_context(self):
        table = Hypercube("solar:InverterPowerLevelTable",
                          ["solar:ProductIdentifierAxis",
                           "solar:InverterPowerLevelPercentAxis"])

        c1 = table.store_context(Context(duration = "forever",
                                         entity = "JUPITER",
                                         ProductIdentifierAxis = "ABCD",
                                         InverterPowerLevelPercentAxis = 50))
        self.assertEqual(c1.get_id(), "solar:InverterPowerLevelTable_0")
        c2 = table.store_context(Context(duration = "forever",
                                         entity = "JUPITER",
                                         ProductIdentifierAxis = "ABCD",
                                         InverterPowerLevelPercentAxis = 50)) # Same
        self.assertIs(c1, c2)
        c3 = table.store_context(Context(duration = "forever",
                                         entity = "JUPITER",
                                         ProductIdentifierAxis = "ABCD",
                                         InverterPowerLevelPercentAxis = 75)) # Different
        self.assertIsNot(c1, c3)


    def test_facts_stored_with_context(self):
        # Test we can store 2 facts of the same concept but with different
        # contexts, and pull them both back out.
        doc = Entrypoint("CutSheet", self.taxonomy)
        concept = "solar:InverterCutSheetNotes"

        ctx_jan = Context(duration={"start": datetime(year=2018, month=1, day=1),
                                   "end": datetime(year=2018, month=2, day=1)},
                          entity="JUPITER",
                          ProductIdentifierAxis= "placeholder",
                          TestConditionAxis = "placeholder")
        ctx_feb = Context(duration={"start": datetime(year=2018, month=2, day=1),
                                   "end": datetime(year=2018, month=3, day=1)},
                          entity="JUPITER",
                          ProductIdentifierAxis= "placeholder",
                          TestConditionAxis = "placeholder")
    
        doc.set(concept, "Jan Value", context=ctx_jan)
        doc.set(concept, "Feb Value", context=ctx_feb)

        jan_fact = doc.get(concept, context=ctx_jan)
        feb_fact = doc.get(concept, context=ctx_feb)

        self.assertEqual(jan_fact.value, "Jan Value")
        self.assertEqual(feb_fact.value, "Feb Value")
                
    # TODO test getting with a mismatching context, should give None.

    def test_conversion_to_xml(self):
        doc = Entrypoint("CutSheet", self.taxonomy)
        doc.set("solar:TypeOfDevice", "Module",
                entity="JUPITER",
                duration="forever",
                ProductIdentifierAxis= "placeholder",
                TestConditionAxis = "placeholder",
                )
        now = datetime.now()
        doc.set("solar:DeviceCost", 100,
                entity="JUPITER",
                instant= now,
                ProductIdentifierAxis= "placeholder",
                TestConditionAxis= "placeholder",
                unit="dollars")
        xml = doc.toXMLString()

        root = etree.fromstring(xml)

        self.assertEqual( len(root.getchildren()), 5)
        # top-level xml should have child <link:schemaRef> and then the other children are contexts and facts
        schemaRef = root.getchildren()[0]
        self.assertEqual( schemaRef.tag, "{http://www.xbrl.org/2003/linkbase}schemaRef" )
        
        contexts = root.findall('{http://www.xbrl.org/2003/instance}context')
        self.assertEqual(len(contexts), 2)

        # Expect to see two facts solar:DeviceCost and solar:TypeOfDevice,
        # each containing text of the fact value
        costFact = root.find('{http://xbrl.us/Solar/v1.2/2018-03-31/solar}DeviceCost')
        typeFact = root.find('{http://xbrl.us/Solar/v1.2/2018-03-31/solar}TypeOfDevice')
        self.assertEqual(costFact.text, "100")
        self.assertEqual(typeFact.text, "Module")
        # They should have contextRef and unitRef attributes:
        self.assertEqual(typeFact.attrib['unitRef'], "None")
        self.assertEqual(typeFact.attrib['contextRef'], "solar:CutSheetDetailsTable_0")
            
        self.assertEqual(costFact.attrib['unitRef'], "dollars")
        self.assertEqual(costFact.attrib['contextRef'], "solar:CutSheetDetailsTable_1")

        
        # expect to see 2 contexts with id "solar:CutSheetDetailsTable_0" and "solar:CutSheetDetailsTable_1"
        # both should have entity tag containing identifier containing text JUPITER
        # both should have segment containing xbrldi:explicitMember dimension="<axis name>" containing text placeholder
        # one should have period containing <forever/> other should have period containing <instant> containing today's date.




    def test_conversion_to_json(self):
        doc = Entrypoint("CutSheet", self.taxonomy)
        doc.set("solar:TypeOfDevice", "Module",
                entity="JUPITER",
                duration="forever",
                ProductIdentifierAxis= "placeholder",
                TestConditionAxis = "placeholder",
                )
        now = datetime.now()
        doc.set("solar:DeviceCost", 100,
                entity="JUPITER",
                instant= now,
                ProductIdentifierAxis= "placeholder",
                TestConditionAxis= "placeholder",
                unit="dollars")
        jsonstring = doc.toJSONString()

        root = json.loads(jsonstring)

        # should have 2 facts:
        self.assertEqual( len(root['facts']), 2)

        # each should have expected 'value' and 'aspects':
        typeFact = root['facts'][1]
        self.assertEqual(typeFact['value'], 'Module')
        
        self.assertEqual(typeFact['aspects']['xbrl:concept'], 'solar:TypeOfDevice')
        self.assertEqual(typeFact['aspects']['solar:ProductIdentifierAxis'], 'placeholder')
        self.assertEqual(typeFact['aspects']['solar:TestConditionAxis'], 'placeholder')
        self.assertEqual(typeFact['aspects']['xbrl:entity'], 'JUPITER')
        self.assertEqual(typeFact['aspects']['xbrl:period'], 'forever')
        self.assertEqual(typeFact['aspects']['xbrl:unit'], 'None')


        costFact = root['facts'][0]
        self.assertEqual(costFact['value'], '100')
        self.assertEqual(costFact['aspects']['xbrl:concept'], 'solar:DeviceCost')
        self.assertEqual(costFact['aspects']['solar:ProductIdentifierAxis'], 'placeholder')
        self.assertEqual(costFact['aspects']['solar:TestConditionAxis'], 'placeholder')
        self.assertEqual(costFact['aspects']['xbrl:entity'], 'JUPITER')
        self.assertEqual(costFact['aspects']['xbrl:instant'], now.strftime("%Y-%m-%d"))
        self.assertEqual(costFact['aspects']['xbrl:unit'], 'dollars')

