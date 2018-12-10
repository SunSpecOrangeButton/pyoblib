# Copyright 2018 Jonathan Xia

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from data_model import Entrypoint, Context, Hypercube, UNTABLE
from datetime import datetime, date
from taxonomy import getTaxonomy
from lxml import etree
import json
from taxonomy import PeriodType

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
        # allowable concepts as defined by the taxonomy for CutSheets.

        # TypeOfDevice is allowed in CutSheets:
        self.assertTrue(doc.can_write_concept('solar:TypeOfDevice'))
        # AppraisalCounterparties is not allowed in CutSheets:
        self.assertFalse(doc.can_write_concept('solar:AppraisalCounterparties'))

        # The newly initialized CutSheet should have a correct list of tables
        # and each table should have a correct list of axes, as defined by
        # the taxonomy for CutSheets:
        tables = doc.get_table_names()
        self._check_arrays_equivalent(tables,
                                      ["solar:InverterPowerLevelTable",
                                       "solar:CutSheetDetailsTable"])
        self._check_arrays_equivalent(
            doc.get_table("solar:InverterPowerLevelTable").axes(),
                         ["solar:ProductIdentifierAxis",
                          "solar:InverterPowerLevelPercentAxis"])
        self._check_arrays_equivalent(
            doc.get_table("solar:CutSheetDetailsTable").axes(),
                         ["solar:ProductIdentifierAxis",
                          "solar:TestConditionAxis"])

    def test_get_table_for_concept(self):
        doc = Entrypoint("CutSheet", self.taxonomy)
        # The CutSheet instance should know that RevenueMeterFrequency
        # is a concept that belongs in the CutSheetDetailsTable
        table = doc.get_table_for_concept("solar:RevenueMeterFrequency")
        self.assertEqual(table.name(), "solar:CutSheetDetailsTable")

        table = doc.get_table_for_concept("solar:InverterEfficiencyAtVmaxPercent")
        self.assertEqual(table.name(), "solar:InverterPowerLevelTable")

        # but if we ask for something that is not a line item concept,
        # we should get back the non-table:
        table = doc.get_table_for_concept("solar:CutSheetDetailsTable")
        self.assertEqual(table.name(), UNTABLE)

    def test_can_write_concept(self):
        doc = Entrypoint("CutSheet", self.taxonomy)

        # Not every concept is writable. For instance, we shouldn't be able
        # to write a value for an Abstract concept, a LineItem group, an Axis,
        # a Domain, etc. even though those are part of this entrypoint.
        self.assertFalse( doc.can_write_concept('solar:ProductIdentifierModuleAbstract'))
        self.assertTrue( doc.can_write_concept('solar:TypeOfDevice'))
        self.assertFalse( doc.can_write_concept('solar:CutSheetDetailsLineItems'))

        self.assertFalse( doc.can_write_concept('solar:CutSheetDetailsTable'))
        self.assertFalse( doc.can_write_concept('solar:TestConditionDomain'))

        self.assertFalse( doc.can_write_concept('solar:ProductIdentifierAxis'))
        self.assertTrue( doc.can_write_concept('solar:ProductIdentifier'))

    def test_sufficient_context_instant_vs_duration(self):
        doc = Entrypoint("CutSheet", self.taxonomy)

        # in order to set a concept value, sufficient context must be
        # provided. what is sufficient context varies by concept.
        # in general the context must provide the correct time information
        # (either duration or instant)

        # We shouldn't even be able to instantiate a context with no time info:
        with self.assertRaises(Exception):
            noTimeContext = Context(ProductIdentifierAxis = "placeholder",
                                    TestConditionAxis= "solar:StandardTestConditionMember")

        # solar:DeviceCost has period_type instant
        # so it requires a context with an instant. A context without an instant
        # should be insufficient:
        instantContext = Context(ProductIdentifierAxis = "placeholder",
                                 TestConditionAxis = "solar:StandardTestConditionMember",
                                 instant = datetime.now())
        durationContext = Context(ProductIdentifierAxis = "placeholder",
                           TestConditionAxis = "solar:StandardTestConditionMember",
                           duration = "forever")

        self.assertTrue( doc.sufficient_context("solar:DeviceCost",
                                                instantContext))
        # A context with a duration instead of an instant should also be
        # rejected:
        with self.assertRaises(Exception):
            doc.sufficient_context("solar:DeviceCost", durationContext)

        # solar:ModuleNameplateCapacity has period_type duration.
        # A context with an instant instead of a duration should also be
        # rejected:
        with self.assertRaises(Exception):
            doc.sufficient_context("solar:ModuleNameplateCapacity", instantContext)
        self.assertTrue( doc.sufficient_context("solar:ModuleNameplateCapacity",
                                               durationContext))


    def test_sufficient_context_axes(self):
        doc = Entrypoint("CutSheet", self.taxonomy)

        # The context must also provide all of the axes needed to place the
        # fact within the right table.

        # DeviceCost is on the CutSheetDetailsTable so it needs a value
        # for ProductIdentifierAxis and TestConditionAxis.
        with self.assertRaises(Exception):
            doc.sufficient_context("solar:DeviceCost", {})

        context = Context(instant = datetime.now(),
                          ProductIdentifierAxis = "placeholder",
                          TestConditionAxis = "solar:StandardTestConditionMember")
        self.assertTrue( doc.sufficient_context("solar:DeviceCost", context) )

        badContext = Context(instant = datetime.now(),
                             TestConditionAxis = "solar:StandardTestConditionMember")
        with self.assertRaises(Exception):
            doc.sufficient_context("solar:DeviceCost", badContext)

        badContext = Context(instant = datetime.now(),
                             ProductIdentifierAxis = "placeholder")
        with self.assertRaises(Exception):
            doc.sufficient_context("solar:DeviceCost", badContext)


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
                          InverterPowerLevelPercentAxis = 'solar:InverterPowerLevel100PercentMember')

        self.assertTrue( doc.sufficient_context(concept, context))

        badContext = Context(instant = datetime.now(),
                             InverterPowerLevelPercentAxis = 'solar:InverterPowerLevel100PercentMember')
        with self.assertRaises(Exception):
            doc.sufficient_context(concept, badContext)

        badContext = Context(instant = datetime.now(),
                             ProductIdentifierAxis = "placeholder")
        with self.assertRaises(Exception):
            doc.sufficient_context(concept, badContext)


    def test_set_separate_dimension_args(self):
        # Tests the case where .set() is called correctly.  Use the
        # way of calling .set() where we pass in every dimension
        # separately. Verify the data is stored and can be retrieved
        # using .get().
        doc = Entrypoint("CutSheet", self.taxonomy)

        # Write a TypeOfDevice and a DeviceCost:

        doc.set("solar:TypeOfDevice", "ModuleMember",
                duration="forever",
                ProductIdentifierAxis= "placeholder",
                TestConditionAxis = "solar:StandardTestConditionMember"
                )
        now = datetime.now()
        doc.set("solar:DeviceCost", 100,
                instant= now,
                ProductIdentifierAxis= "placeholder",
                TestConditionAxis= "solar:StandardTestConditionMember",
                unit_name="USD")

        typeFact = doc.get("solar:TypeOfDevice",
                        Context(duration="forever",
                                ProductIdentifierAxis= "placeholder",
                                TestConditionAxis = "solar:StandardTestConditionMember"))
        self.assertEqual( typeFact.value,  "ModuleMember")
        costFact = doc.get("solar:DeviceCost",
                           Context(instant = now,
                                ProductIdentifierAxis= "placeholder",
                                TestConditionAxis = "solar:StandardTestConditionMember"))
        self.assertEqual( costFact.value, 100)
        self.assertEqual( costFact.unit, "USD")

    def test_set_context_arg(self):
        # Tests the case where .set() is called correctly, using
        # the way of calling .set() where we pass in a Context
        # object. Verify the data is stored and can be retrieved
        # using .get().
        doc = Entrypoint("CutSheet", self.taxonomy)
        ctx = Context(duration="forever",
                      entity="JUPITER",
                      ProductIdentifierAxis= "placeholder",
                      TestConditionAxis = "solar:StandardTestConditionMember")
        doc.set("solar:TypeOfDevice", "ModuleMember", context=ctx)

        now = datetime.now(),
        ctx = Context(instant= now,
                      entity="JUPITER",
                      ProductIdentifierAxis= "placeholder",
                      TestConditionAxis = "solar:StandardTestConditionMember")
        doc.set("solar:DeviceCost", 100, context=ctx, unit_name="USD")

        # Get the data bacK:
        typeFact = doc.get("solar:TypeOfDevice",
                        Context(duration="forever",
                                entity="JUPITER",
                                ProductIdentifierAxis= "placeholder",
                                TestConditionAxis = "solar:StandardTestConditionMember"))
        self.assertEqual( typeFact.value,  "ModuleMember")
        costFact = doc.get("solar:DeviceCost",
                           Context(instant = now,
                                entity="JUPITER",
                                ProductIdentifierAxis= "placeholder",
                                TestConditionAxis = "solar:StandardTestConditionMember"))
        self.assertEqual( costFact.value, 100)


    def test_set_raises_exception(self):
        # Tests the case where .set() is called incorrectly. It should
        # raise exceptions if required information is missing.
        doc = Entrypoint("CutSheet", self.taxonomy)
        with self.assertRaises(Exception):
            doc.set("solar:TypeOfDevice", "ModuleMember", {})

        with self.assertRaises(Exception):
            doc.set("solar:DeviceCost", 100, {})

    def test_hypercube_store_context(self):
        doc = Entrypoint("CutSheet", self.taxonomy)
        table = doc.get_table("solar:InverterPowerLevelTable")

        c1 = table.store_context(Context(duration = "forever",
                                         entity = "JUPITER",
                                         ProductIdentifierAxis = "ABCD",
                                         InverterPowerLevelPercentAxis = 'solar:InverterPowerLevel50PercentMember'))
        self.assertEqual(c1.get_id(), "solar:InverterPowerLevelTable_0")
        c2 = table.store_context(Context(duration = "forever",
                                         entity = "JUPITER",
                                         ProductIdentifierAxis = "ABCD",
                                         InverterPowerLevelPercentAxis = 'solar:InverterPowerLevel50PercentMember')) # Same
        self.assertIs(c1, c2)
        c3 = table.store_context(Context(duration = "forever",
                                         entity = "JUPITER",
                                         ProductIdentifierAxis = "ABCD",
                                         InverterPowerLevelPercentAxis = 'solar:InverterPowerLevel75PercentMember')) # Different
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
                          TestConditionAxis = "solar:StandardTestConditionMember")
        ctx_feb = Context(duration={"start": datetime(year=2018, month=2, day=1),
                                   "end": datetime(year=2018, month=3, day=1)},
                          entity="JUPITER",
                          ProductIdentifierAxis= "placeholder",
                          TestConditionAxis = "solar:StandardTestConditionMember")
    
        doc.set(concept, "Jan Value", context=ctx_jan)
        doc.set(concept, "Feb Value", context=ctx_feb)

        jan_fact = doc.get(concept, context=ctx_jan)
        feb_fact = doc.get(concept, context=ctx_feb)

        self.assertEqual(jan_fact.value, "Jan Value")
        self.assertEqual(feb_fact.value, "Feb Value")
                
    # TODO test getting with a mismatching context, should give None.

    def test_conversion_to_xml(self):
        doc = Entrypoint("CutSheet", self.taxonomy)
        doc.set("solar:TypeOfDevice", "ModuleMember",
                entity="JUPITER",
                duration="forever",
                ProductIdentifierAxis= "placeholder",
                TestConditionAxis = "solar:StandardTestConditionMember"
                )
        now = datetime.now()
        doc.set("solar:DeviceCost", 100,
                entity="JUPITER",
                instant= now,
                ProductIdentifierAxis= "placeholder",
                TestConditionAxis= "solar:StandardTestConditionMember",
                unit_name="USD")
        xml = doc.to_XML_string()
        root = etree.fromstring(xml)


        self.assertEqual( len(root.getchildren()), 6)
        # top-level xml should have child <link:schemaRef>, one <unit>, two <context>s and two <fact>s.
        schemaRef = root.getchildren()[0]
        self.assertEqual( schemaRef.tag, "{http://www.xbrl.org/2003/linkbase}schemaRef" )

        # expect to see 2 contexts with id "solar:CutSheetDetailsTable_0" and "solar:CutSheetDetailsTable_1"
        contexts = root.findall('{http://www.xbrl.org/2003/instance}context')
        self.assertEqual(len(contexts), 2)
        for context in contexts:
            # both should have entity tag containing identifier containing text JUPITER
            self.assertTrue( context.attrib["id"] == 'solar:CutSheetDetailsTable_0' or \
                             context.attrib["id"] == 'solar:CutSheetDetailsTable_1' )

            entity = context.find("{http://www.xbrl.org/2003/instance}entity")
            identifier = entity.find("{http://www.xbrl.org/2003/instance}identifier")
            self.assertEqual(identifier.text, "JUPITER")
            
            # both should have segment containing xbrldi:explicitMember dimension="<axis name>"
            # containing text "placeholder"
            # (wait i have segment inside of entity?  is that correct?)
            segment = entity.find("{http://www.xbrl.org/2003/instance}segment")

            axes = segment.findall("{http://xbrl.org/2006/xbrldi}typedMember")
            axis_names = [x.attrib["dimension"] for x in axes]

            self._check_arrays_equivalent(axis_names, ['solar:ProductIdentifierAxis',
                                                       'solar:TestConditionAxis'])
            for axis in axes:
                if axis.attrib["dimension"] == 'solar:ProductIdentifierAxis':
                    self.assertEqual(axis.getchildren()[0].tag, "{http://xbrl.us/Solar/v1.2/2018-03-31/solar}ProductIdentifierDomain")
                    self.assertEqual(axis.getchildren()[0].text, "placeholder")
                elif axis.attrib["dimension"] == 'solar:TestConditionsAxis':
                    self.assertEqual(axis.getchildren()[0].tag, "{http://xbrl.us/Solar/v1.2/2018-03-31/solar}TestConditionDomain")
                    self.assertEqual(axis.getchildren()[0].text, "solar:StandardTestConditionMember")

            # one should have period containing <forever/> other should have period containing <instant> containing today's date.
            period = context.find("{http://www.xbrl.org/2003/instance}period")
            tag = period.getchildren()[0].tag
            self.assertTrue(tag == "{http://www.xbrl.org/2003/instance}instant" or\
                            tag == "{http://www.xbrl.org/2003/instance}forever")

        # Expect one unit tag with id=USD containing <measure>units:USD</measure>
        unit_tag = root.findall("{http://www.xbrl.org/2003/instance}unit")
        self.assertEqual(len(unit_tag), 1)
        self.assertEqual(unit_tag[0].attrib["id"], "USD")
        self.assertEqual(unit_tag[0].getchildren()[0].text, "units:USD")

        # Expect to see two facts solar:DeviceCost and solar:TypeOfDevice,
        # each containing text of the fact value
        costFact = root.find('{http://xbrl.us/Solar/v1.2/2018-03-31/solar}DeviceCost')
        typeFact = root.find('{http://xbrl.us/Solar/v1.2/2018-03-31/solar}TypeOfDevice')
        self.assertEqual(costFact.text, "100")
        self.assertEqual(typeFact.text, "ModuleMember")
        # They should have contextRef and (in the case of cost) unitRef attributes:
        self.assertEqual(typeFact.attrib['contextRef'], "solar:CutSheetDetailsTable_0")
        self.assertEqual(costFact.attrib['unitRef'], "USD")
        self.assertEqual(costFact.attrib['contextRef'], "solar:CutSheetDetailsTable_1")
        # TODO should TypeOfDevice have unitRef = "None" or should it not have a unitRef?
        # i'm assuming the latter.


    def test_conversion_to_json(self):
        doc = Entrypoint("CutSheet", self.taxonomy)
        doc.set("solar:TypeOfDevice", "ModuleMember",
                entity="JUPITER",
                duration="forever",
                ProductIdentifierAxis= "placeholder",
                TestConditionAxis = "solar:StandardTestConditionMember",
                )
        now = datetime.now()
        doc.set("solar:DeviceCost", 100,
                entity="JUPITER",
                instant= now,
                ProductIdentifierAxis= "placeholder",
                TestConditionAxis= "solar:StandardTestConditionMember",
                unit_name="USD")
        jsonstring = doc.to_JSON_string()

        root = json.loads(jsonstring)

        # should have 2 facts:
        self.assertEqual( len(root['facts']), 2)

        # each should have expected 'value' and 'aspects':
        typeFacts = [x for x in root['facts'] if x['aspects']['xbrl:concept'] == 'solar:TypeOfDevice']
        self.assertEqual(len(typeFacts), 1)
        typeFact = typeFacts[0]
        self.assertEqual(typeFact['value'], "ModuleMember")
        self.assertEqual(typeFact['aspects']['solar:ProductIdentifierAxis'], 'placeholder')
        self.assertEqual(typeFact['aspects']['solar:TestConditionAxis'],
                             "solar:StandardTestConditionMember")
        self.assertEqual(typeFact['aspects']['xbrl:entity'], 'JUPITER')
        self.assertEqual(typeFact['aspects']['xbrl:period'], 'forever')
        # TODO if there's no unit is it correct to write 'xbrl:unit':'None' or to leave out
        # xbrl:unit?  Currently assuming we leave it out:
        self.assertNotIn("xbrl:unit", typeFact["aspects"])

        costFacts = [x for x in root['facts'] if x['aspects']['xbrl:concept'] == 'solar:DeviceCost']
        self.assertEqual(len(costFacts), 1)

        costFact = costFacts[0]
        self.assertEqual(costFact['value'], '100')
        self.assertEqual(costFact['aspects']['solar:ProductIdentifierAxis'], 'placeholder')
        self.assertEqual(costFact['aspects']['solar:TestConditionAxis'],
                             "solar:StandardTestConditionMember")
        self.assertEqual(costFact['aspects']['xbrl:entity'], 'JUPITER')
        self.assertEqual(costFact['aspects']['xbrl:instant'], now.strftime("%Y-%m-%d"))
        self.assertEqual(costFact['aspects']['xbrl:unit'], 'USD')


    def test_concepts_load_metadata(self):
        doc = Entrypoint("CutSheet", self.taxonomy)

        frequency = doc.get_concept_by_name("solar:RevenueMeterFrequency")
        device = doc.get_concept_by_name("solar:TypeOfDevice")

        # Metadata such as period-type, type-name, and nillable should be available
        # on the concept objects:
        self.assertEqual(frequency.get_metadata("period_type"), PeriodType.duration)
        self.assertEqual(frequency.get_metadata("type_name"), "num-us:frequencyItemType")
        self.assertEqual(frequency.get_metadata("nillable"), True)

        self.assertEqual(device.get_metadata("period_type"), PeriodType.duration)
        self.assertEqual(device.get_metadata("type_name"), "solar-types:deviceItemType")
        self.assertEqual(device.get_metadata("nillable"), True)

        # Parents and children should be correct:
        self.assertEqual(device.parent.name, 'solar:CutSheetDetailsLineItems')
        self.assertEqual(frequency.parent.name, 'solar:ProductIdentifierMeterAbstract')
        self.assertEqual(len(device.children), 0)
        self.assertEqual(len(frequency.children), 0)


    def test_hypercube_can_identify_axis_domains(self):
        doc = Entrypoint("CutSheet", self.taxonomy)
        table = doc.get_table("solar:CutSheetDetailsTable")

        domain = table.get_domain("solar:ProductIdentifierAxis")
        self.assertEqual(domain, "solar:ProductIdentifierDomain")

        domain = table.get_domain("solar:TestConditionAxis")
        self.assertEqual(domain, "solar:TestConditionDomain")

        # TODO add a test for an axis that is explicit and not domain-based


    def test_hypercube_rejects_out_of_domain_axis_values(self):
        # Try passing in something as a value for TestConditionAxis that is not
        # one of the enumerated Members; it should be rejected:

        doc = Entrypoint("CutSheet", self.taxonomy)
        table = doc.get_table("solar:CutSheetDetailsTable")

        self.assertTrue( table.axis_value_within_domain("solar:TestConditionAxis",
                                                     "solar:StandardTestConditionMember") )

        self.assertFalse( table.axis_value_within_domain("solar:TestConditionAxis",
                                                     "solar:InverterPowerLevel100PercentMember"))

        concept = 'solar:InverterOutputRatedPowerAC'
        context = Context(duration = "forever",
                          ProductIdentifierAxis = "placeholder",
                          InverterPowerLevelPercentAxis = 'solar:StandardTestConditionMember')
        # not a valid value for InverterPowerLevelPercentAxis
        with self.assertRaises(Exception):
            doc.sufficient_context(concept, context)


    def test_reject_missing_or_invalid_units(self):
        # issue #28
        # -- reject attempt to set a fact if it doesn't have a unit and the unit is required
        # -- reject attempt to set a fact using a unit name that doesn't match taxonomy
        # -- reject attempt to set a fact using a unit that is the wrong type
        now = datetime.now()
        doc = Entrypoint("CutSheet", self.taxonomy)
        with self.assertRaises(Exception):
            # Unit is required but not provided, so this should fail:
            doc.set("solar:DeviceCost", 100,
                entity="JUPITER",
                instant= now,
                ProductIdentifierAxis= "placeholder",
                TestConditionAxis= "solar:StandardTestConditionMember")

        with self.assertRaises(Exception):
            # Zorkmids is not a real unit, so this should fail:
            doc.set("solar:DeviceCost", 100,
                entity="JUPITER",
                instant= now,
                ProductIdentifierAxis= "placeholder",
                TestConditionAxis= "solar:StandardTestConditionMember",
                unit_name="zorkmids")

        with self.assertRaises(Exception):
            # kWh is a real unit but the wrong type, so this should fail:
            doc.set("solar:DeviceCost", 100,
                entity="JUPITER",
                instant= now,
                ProductIdentifierAxis= "placeholder",
                TestConditionAxis= "solar:StandardTestConditionMember",
                unit_name="kWh")

        # USD is a valid unit, so this should succeed:
        doc.set("solar:DeviceCost", 100,
                entity="JUPITER",
                instant= now,
                ProductIdentifierAxis= "placeholder",
                TestConditionAxis= "solar:StandardTestConditionMember",
                unit_name="USD")

    def test_valid_unit_method(self):
        doc = Entrypoint("CutSheet", self.taxonomy)
        # Basic data types:
        self.assertTrue( doc.valid_unit("solar:TrackerNumberOfControllers", None)) # pure integer
        self.assertTrue( doc.valid_unit("solar:TransformerStyle", None)) # string
        self.assertTrue( doc.valid_unit("solar:TransformerDesignFactor", None)) # decimal
        self.assertTrue( doc.valid_unit("solar:MeterRevenueGrade", None)) # boolean

        # Advanced data types:
        self.assertTrue( doc.valid_unit("solar:DeviceCost", "USD")) # xbrli:monetaryItemType
        self.assertTrue( doc.valid_unit("solar:CutSheetDocumentLink", None)) #:xbrlianyURIItemType
        self.assertTrue( doc.valid_unit("solar:CECListingDate", None)) #xbrli:dateItemType
        self.assertTrue( doc.valid_unit("solar:InverterHarmonicsTheshold", None)) #num:percentItemType

        # Physics data types:
        self.assertTrue( doc.valid_unit("solar:RevenueMeterFrequency", "Hz")) #num-us:frequencyItemType
        self.assertTrue( doc.valid_unit("solar:InverterWidth", "cm")) #:num:lengthItemType
        self.assertTrue( doc.valid_unit("solar:BatteryRating", "kW")) #:num:powerItemType
        self.assertTrue( doc.valid_unit("solar:InverterInputMaximumOperatingCurrentDC", "A")) #:num-us:electricCurrentItemType
        self.assertTrue( doc.valid_unit("solar:InverterInputMaximumVoltageDC", "V")) #:num-us:voltageItemType
        self.assertTrue( doc.valid_unit("solar:InverterOperatingTemperatureRangeMaximum", "Cel")) #:num-us:temperatureItemType
        # self.assertTrue( doc.valid_unit("solar:TrackerStowWindSpeed:num-us:speedItemType", "???"))
        self.assertTrue( doc.valid_unit("solar:OrientationMaximumTrackerRotationLimit", "Degree")) #:num-us:planeAngleItemType
        
        self.assertTrue( doc.valid_unit("solar:TrackerStyle", None)) #solar-types:trackerItemType
        self.assertTrue( doc.valid_unit("solar:BatteryStyle", None)) #solar-types:batteryChemistryItemType
        self.assertTrue( doc.valid_unit("solar:TypeOfDevice", None)) #solar-types:deviceItemType


    def test_concepts_can_type_check(self):
        # Try passing in wrong data type to a typed concept:
        doc = Entrypoint("CutSheet", self.taxonomy)
        concept = doc.get_concept_by_name("solar:TrackerNumberOfControllers") # integer
        self.assertTrue(concept.validate_datatype("3"))
        self.assertFalse(concept.validate_datatype("3.5"))
        self.assertFalse(concept.validate_datatype("a few"))

        concept = doc.get_concept_by_name("solar:TransformerStyle") # string
        self.assertTrue(concept.validate_datatype("Autobot"))
        self.assertTrue(concept.validate_datatype("Decepticon"))
        self.assertFalse(concept.validate_datatype(99.99))

        concept = doc.get_concept_by_name("solar:TransformerDesignFactor") # decimal
        self.assertTrue(concept.validate_datatype("0.99"))
        self.assertTrue(concept.validate_datatype("1"))
        self.assertFalse(concept.validate_datatype("pretty good"))

        concept = doc.get_concept_by_name("solar:MeterRevenueGrade") # boolean
        self.assertTrue(concept.validate_datatype("True"))
        self.assertTrue(concept.validate_datatype("False"))
        self.assertTrue(concept.validate_datatype(True))
        self.assertTrue(concept.validate_datatype(False))
        self.assertFalse(concept.validate_datatype("yes"))
        self.assertFalse(concept.validate_datatype("7"))

    def test_reject_invalid_datatype(self):
        doc = Entrypoint("CutSheet", self.taxonomy)
        with self.assertRaises(Exception):
            # A non-integer is given, this should fail:
            doc.set("solar:TrackerNumberOfControllers", 0.5,
                entity="JUPITER",
                duration="forever",
                ProductIdentifierAxis= "placeholder",
                TestConditionAxis= "solar:StandardTestConditionMember")

        with self.assertRaises(Exception):
            # A string that can't be parsed into an integer should fail:
            doc.set("solar:TrackerNumberOfControllers", "abcdefg",
                entity="JUPITER",
                duration="forever",
                ProductIdentifierAxis= "placeholder",
                TestConditionAxis= "solar:StandardTestConditionMember")

        # But a string that can be parsed into an integer should succeed:
        doc.set("solar:TrackerNumberOfControllers", "2",
                entity="JUPITER",
                duration="forever",
                ProductIdentifierAxis= "placeholder",
                TestConditionAxis= "solar:StandardTestConditionMember")


    def test_hypercube_rejects_context_with_unwanted_axes(self):
        # Test that giving a context an *extra* axis that is invalid for the table
        # causes it to be rejected as well.
        doc = Entrypoint("CutSheet", self.taxonomy)

        twoAxisContext = Context(ProductIdentifierAxis = "placeholder",
                                 TestConditionAxis = "solar:StandardTestConditionMember",
                                 instant = datetime.now())
        self.assertTrue( doc.sufficient_context("solar:DeviceCost",
                                                twoAxisContext))

        threeAxisContext = Context(
            ProductIdentifierAxis = "placeholder",
            InverterPowerLevelPercentAxis = 'solar:InverterPowerLevel50PercentMember',
            TestConditionAxis = "solar:StandardTestConditionMember",
            instant = datetime.now())
        # InverterPowerLevelPercentAxis is a valid axis and this is a valid value for it,
        # but the table that holds DeviceCost doesn't want this axis:
        with self.assertRaises(Exception):
            doc.sufficient_context("solar:DeviceCost", threeAxisContext)


    def test_set_default_context_values(self):
        # Test setting default values, for example something like:
        doc = Entrypoint("CutSheet", self.taxonomy)
        now = datetime.now()
        doc.set_default_context({"entity": "JUPITER",
                               "solar:TestConditionAxis": "solar:StandardTestConditionMember",
                               PeriodType.instant: now,
                               PeriodType.duration: "forever"
                               })
        # Could also support setting default unit, even though that's not part of context:
        
        
        # If we set a fact that wants an instant context, it should use 'now':
        doc.set("solar:DeviceCost", "100", unit_name="USD", ProductIdentifierAxis = "placeholder")
        # This would normally raise an exception because it's missing instant, entity, and
        # TestConditionAxis. But we set defaults for those, so they should be filled in:
        fact = doc.get("solar:DeviceCost", Context(
            ProductIdentifierAxis = "placeholder",
            TestConditionAxis = "solar:StandardTestConditionMember",
            entity = "JUPITER",
            instant = now))
        self.assertEqual(fact.value, "100")
        self.assertEqual(fact.unit, "USD")
        self.assertEqual(fact.context.entity, "JUPITER")
        self.assertEqual(fact.context.instant, now)

        # TODO test method of calling set() where we pass in Context object.

        # If we set a fact that wants a duration context, it should use jan 1 - jan 31:
        doc.set("solar:ModuleNameplateCapacity", "0.3", unit_name="W",
                 ProductIdentifierAxis = "placeholder")
        # Would normally raise an exception because missing duration, entity, and
        # TestConditionAxis. But we set defaults for those, so they should be filled in:
        fact = doc.get("solar:ModuleNameplateCapacity", Context(
            ProductIdentifierAxis = "placeholder",
            TestConditionAxis = "solar:StandardTestConditionMember",
            entity = "JUPITER",
            duration = "forever"))
        self.assertEqual(fact.value, "0.3")
        self.assertEqual(fact.unit, "W")
        self.assertEqual(fact.context.entity, "JUPITER")
        self.assertEqual(fact.context.duration, "forever")
        

        # Try setting ALL the fields in set_default_context and then pass in NO context fields,
        # that should work too:
        doc.set_default_context({"entity": "JUPITER",
                               "solar:TestConditionAxis": "solar:StandardTestConditionMember",
                               PeriodType.instant: now,
                               "solar:ProductIdentifierAxis": "placeholder"
                               })
        doc.set("solar:DeviceCost", "99", unit_name="USD")
        fact = doc.get("solar:DeviceCost", Context(
            ProductIdentifierAxis = "placeholder",
            TestConditionAxis = "solar:StandardTestConditionMember",
            entity = "JUPITER",
            instant = now))
        self.assertEqual(fact.value, "99")


    def test_tableless_facts(self):
        # Some entry points, like MonthlyOperatingReport, seem to have concepts
        # in them that are not part of any table:
        doc = Entrypoint("MonthlyOperatingReport", self.taxonomy)

        doc.set("solar:MonthlyOperatingReportEffectiveDate",
                date(year=2018,month=6,day=1),
                entity = "JUPITER",
                duration="forever")

        fact = doc.get("solar:MonthlyOperatingReportEffectiveDate",
                       Context(entity = "JUPITER",
                               duration="forever"))

        self.assertEqual(fact.value, date(year=2018,month=6,day=1))

    # TODO try a test where we give somethign a duration like:
    #  {"start": date(year=2018,month=1,day=1),
    #   "end": date(year=2018,month=1,day=31)}
    # and then look up the fact and make sure it has that start and end date.

    # TODO test conversion to XML and JSON when duration has start and end.

    def test_validate_values_for_enumerated_solar_data_types(self):
        # solar-specific data types (Defined in a document we don't have:
        # xmlns:solar-types="http://xbrl.us/dtr/type/solar-types"
        # namespace="http://xbrl.us/dtr/type/solar-types"
        # schemaLocation="solar-types-2018-03-31.xsd"/>

        # OK we have that document but we don't load it?

        # in solar-types-2018-03-31.xsd there is a <complexType tag name="deviceItemType">
        # has <simpleContent> which has <restriction> which hasa bunch of <xs:enumeration>
        # each of which has a value like "ModuleMember", "OptimizerMember", etc.
        pass



