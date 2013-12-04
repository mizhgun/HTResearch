# stdlib imports
import unittest
from springpython.context import ApplicationContext
from springpython.config import Object

# project imports
from HTResearch.WebCrawler.WebCrawler.items import ScrapedOrganization, ScrapedContact
from HTResearch.Utilities.context import ItemPipelineContext
from HTResearch.DataModel.enums import OrgTypesEnum
from HTResearch.Test.Mocks.connection import MockDBConnection
from HTResearch.Test.Mocks.dao import *


class TestablePipelineContext(ItemPipelineContext):
    @Object()
    def RegisteredDBConnection(self):
        return MockDBConnection


class ItemPipelineTest(unittest.TestCase):
    def setUp(self):
        print "New ItemPipelineTest running"

        self.org = ScrapedOrganization(
            name="Yoyodyne",
            address="1234 Yoyodyne Way, San Narciso, CA",
            types=[OrgTypesEnum.GOVERNMENT, OrgTypesEnum.RESEARCH],
            phone_numbers=["4026170423"],
            emails=["info@yoyodyne.com"],
            contacts=[],
            organization_url="www.yoyodyne.com",
            partners=[
                {'organization_url': 'http://www.acumenfund.org/'},
                {'organization_url': 'http://www.afghaninstituteoflearning.org/'},
                {'organization_url': 'http://www.prajwalaindia.com/'},
                {'organization_url': 'http://www.mencanstoprape.org/'},
                {'organization_url': 'http://novofoundation.org/'},
            ]
        )

        self.contact = ScrapedContact(
            first_name="Djordan",
            last_name="Jdegner",
            phone=5555555555,
            email='djordan@jdegner.com',
            organization='Yoyodyne',
            position='Software Jdeveloper'
        )

        self.ctx = ApplicationContext(TestablePipelineContext())

    def tearDown(self):
        with MockDBConnection() as db:
            db.dropall()

    def test_switch_scraped_org(self):

        print "Creating ItemSwitch"
        item_switch = self.ctx.get_object("ItemSwitch")

        print 'Passing ScrapedOrganization to ItemSwitch'
        print 'NOTE: Passing "None" as spider as it is not used'
        org = item_switch.process_item(self.org, None)

        print 'Testing return value from item_switch'
        self.assertEqual(org, self.org, "Expected value {0} != {1}".format(org, self.org))

        print 'Grabbing stored organization from database'
        org_dao = self.ctx.get_object("OrganizationDAO")

        assert_org = org_dao.find(name=self.org['name'])

        print 'Check that entry is retrievable'
        self.assertIsNotNone(assert_org)

        print 'Testing equality...'
        self.assertEqual(assert_org.name, self.org['name'])
        self.assertEqual(assert_org.organization_url, self.org['organization_url'])
        self.assertEqual(assert_org.emails, self.org['emails'])
        self.assertEqual(assert_org.phone_numbers, self.org['phone_numbers'])
        partners = []
        for partner in assert_org.partners:
            partners.append({'organization_url': partner.organization_url})
        for partner in partners:
            self.assertIn(partner, self.org['partners'])

        print "Item Switch Test Passed"

    def test_switch_scraped_contact(self):

        print "Creating ItemSwitch"
        item_switch = self.ctx.get_object("ItemSwitch")

        print 'Passing ScrapedContact to ItemSwitch'
        print 'NOTE: Passing "None" as spider as it is not used'
        contact = item_switch.process_item(self.contact, None)

        print 'Testing return value from item_switch'
        self.assertEqual(contact, self.contact, "Expected value {0} != {1}".format(contact, self.contact))

        print 'Grabbing stored contact from database'
        contact_dao = self.ctx.get_object("ContactDAO")

        assert_contact = contact_dao.find(first_name=self.contact['first_name'])

        print 'Check that entry is retrievable'
        self.assertIsNotNone(assert_contact)

        print 'Testing equality...'
        self.assertEqual(assert_contact.first_name, self.contact['first_name'])
        self.assertEqual(assert_contact.last_name, self.contact['last_name'])
        self.assertEqual(assert_contact.organization.name, self.contact['organization'])
        self.assertEqual(assert_contact.email, self.contact['email'])
        self.assertEqual(assert_contact.phone, self.contact['phone'])
        self.assertEqual(assert_contact.position, self.contact['position'])

        print "Item Switch Test Passed"

if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0]:
            raise
