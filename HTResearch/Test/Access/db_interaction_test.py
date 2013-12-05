# stdlib imports
import unittest
from springpython.context import ApplicationContext
from springpython.config import Object

# project imports
from HTResearch.DataAccess.dto import *
from HTResearch.DataModel.model import *
from HTResearch.Utilities.converter import DTOConverter
from HTResearch.Utilities.context import DAOContext
from HTResearch.Test.Mocks.connection import MockDBConnection
from HTResearch.Test.Mocks.dao import *
from HTResearch.DataModel.enums import AccountType


class TestableDAOContext(DAOContext):

    @Object()
    def RegisteredDBConnection(self):
        return MockDBConnection

    @Object()
    def RegisteredContactDAO(self):
        return MockContactDAO

    @Object()
    def RegisteredOrganizationDAO(self):
        return MockOrganizationDAO

    @Object()
    def RegisteredPublicationDAO(self):
        return MockPublicationDAO

    @Object()
    def RegisteredURLMetadataDAO(self):
        return MockURLMetadataDAO

    @Object()
    def RegisteredGeocode(self):
        return lambda x: [0.0, 0.0]

class DatabaseInteractionTest(unittest.TestCase):

    def setUp(self):
        print "New DatabaseInteractionTest running"

        self.contact = Contact(first_name="Jordan",
                               last_name="Degner",
                               email="jdegner0129@gmail.com")
        self.organization = Organization(name="Yee University",
                                         organization_url="http://com.bee.yee",
                                         contacts=[self.contact],
                                         email_key="bee@yee.com",
                                         emails=["info@yee.com", "stuff@yee.com"],
                                         phone_numbers=[5555555555, "(555)555-5555"],
                                         facebook="http://www.facebook.com/yee",
                                         twitter="http://www.twitter.com/yee"
                                         )
        self.publication = Publication(title="The Book of Yee",
                                       authors=[self.contact])
        self.urlmetadata = URLMetadata(url="http://google.com")
        self.user = User(first_name="Bee", last_name="Yee",
                         email="beeyee@yee.com", password="iambeeyee",
                         background="I love bees and yees",
                         account_type=AccountType.BASIC)

        self.ctx = ApplicationContext(TestableDAOContext())

    def tearDown(self):
        with MockDBConnection() as db:
            db.dropall()

    def test_contact_dao(self):
        contact_dto = DTOConverter.to_dto(ContactDTO, self.contact)
        contact_dao = self.ctx.get_object("ContactDAO")

        print 'Testing contact creation ...'
        contact_dao.create_update(contact_dto)

        assert_contact = contact_dao.find(id=contact_dto.id,
                                          first_name=contact_dto.first_name,
                                          last_name=contact_dto.last_name,
                                          email=contact_dto.email)
        self.assertEqual(assert_contact.first_name, contact_dto.first_name)
        self.assertEqual(assert_contact.last_name, contact_dto.last_name)
        self.assertEqual(assert_contact.email, contact_dto.email)

        print 'Testing contact editing ...'
        contact_dto.first_name = "Djordan"
        contact_dao.create_update(contact_dto)

        assert_contact = contact_dao.find(id=contact_dto.id,
                                          first_name=contact_dto.first_name)
        self.assertEqual(assert_contact.first_name, contact_dto.first_name)

        print 'Testing contact deletion ...'
        contact_dao.delete(contact_dto)

        assert_contact = contact_dao.find(id=contact_dto.id)
        self.assertTrue(assert_contact is None)

        print 'ContactDAO tests passed'

    def test_organization_dao(self):
        org_dto = DTOConverter.to_dto(OrganizationDTO, self.organization)
        org_dao = self.ctx.get_object("OrganizationDAO")

        print 'Testing organization creation ...'
        org_dao.create_update(org_dto)

        assert_org = org_dao.find(id=org_dto.id,
                                  name=org_dto.name,
                                  organization_url=org_dto.organization_url,
                                  email_key=org_dto.email_key,
                                  emails=org_dto.emails,
                                  phone_numbers=org_dto.phone_numbers,
                                  facebook=org_dto.facebook,
                                  twitter=org_dto.twitter)
        self.assertEqual(assert_org.name, org_dto.name)
        self.assertEqual(assert_org.organization_url, org_dto.organization_url)
        self.assertEqual(assert_org.contacts, org_dto.contacts)
        self.assertEqual(assert_org.email_key, org_dto.email_key)
        self.assertEqual(assert_org.emails, org_dto.emails)
        self.assertEqual(assert_org.phone_numbers, org_dto.phone_numbers)
        self.assertEqual(assert_org.facebook, org_dto.facebook)
        self.assertEqual(assert_org.twitter, org_dto.twitter)

        print 'Testing organization text search ...'

        assert_orgs = org_dao.text_search(num_elements=10, text='bEe YeE university ers')
        self.assertEqual(assert_orgs[0].name, org_dto.name)

        assert_orgs = org_dao.text_search(num_elements=10, text='yee adfgh905w')
        self.assertEqual(assert_orgs, [])

        print 'Testing organization editing ...'
        org_dto.name = "Yee Universityee"
        org_dto.contacts = []
        org_dao.create_update(org_dto)

        assert_org = org_dao.find(id=org_dto.id,
                                  name=u'Yee Universityee')
        self.assertEqual(assert_org.name, org_dto.name)
        self.assertEqual(assert_org.organization_url, org_dto.organization_url)
        self.assertEqual(assert_org.contacts, org_dto.contacts)

        print 'Testing organization deletion ...'
        org_dao.delete(org_dto)

        assert_org = org_dao.find(id=org_dto.id)
        self.assertTrue(assert_org is None)

        print 'OrganizationDAO tests passed'

    def test_publication_dao(self):
        pub_dto = DTOConverter.to_dto(PublicationDTO, self.publication)
        pub_dao = self.ctx.get_object("PublicationDAO")

        print 'Testing publication creation ...'
        pub_dao.create_update(pub_dto)

        assert_pub = pub_dao.find(id=pub_dto.id,
                                  title=pub_dto.title)
        self.assertEqual(assert_pub.title, pub_dto.title)
        self.assertEqual(assert_pub.authors, pub_dto.authors)

        print 'Testing publication editing ...'
        pub_dto.title = "The Book of Mee"
        pub_dao.create_update(pub_dto)

        assert_pub = pub_dao.find(id=pub_dto.id,
                                  title=pub_dto.title)
        self.assertEqual(assert_pub.title, pub_dto.title)

        print 'Testing publication deletion ...'
        pub_dao.delete(pub_dto)

        assert_pub = pub_dao.find(id=pub_dto.id)
        self.assertTrue(assert_pub is None)

        print 'PublicationDAO tests passed'

    def test_urlmetadata_dao(self):
        url_dto = DTOConverter.to_dto(URLMetadataDTO, self.urlmetadata)
        url_dao = self.ctx.get_object("URLMetadataDAO")

        print 'Testing URL creation ...'
        url_dao.create_update(url_dto)

        assert_url = url_dao.find(id=url_dto.id,
                                  url=url_dto.url)
        self.assertEqual(assert_url.url, url_dto.url)

        print 'Testing URL editing ...'
        url_dto.url = "http://facebook.com"
        url_dao.create_update(url_dto)

        assert_url = url_dao.find(id=url_dto.id,
                                  url=url_dto.url)
        self.assertEqual(assert_url.url, url_dto.url)

        print 'Testing URL deletion ...'
        url_dao.delete(url_dto)

        assert_url = url_dao.find(id=url_dto.id)
        self.assertTrue(assert_url is None)

        print 'URLMetadataDAO tests passed'

    def test_user_dao(self):
        user_dto = DTOConverter.to_dto(UserDTO, self.user)
        user_dao = self.ctx.get_object("UserDAO")

        print 'Testing user creation ...'
        user_dao.create_update(user_dto)

        assert_user = user_dao.find(id=user_dto.id)

        self.assertEqual(assert_user.id, user_dto.id)

        print 'Testing user editing ...'
        user_dto.first = "Byee"
        user_dto.last = "Ybee"

        user_dao.create_update(user_dto)

        assert_user = user_dao.find(id=user_dto.id)

        self.assertEqual(assert_user.id, user_dto.id)
        self.assertEqual(assert_user.first_name, user_dto.first_name)
        self.assertEqual(assert_user.last_name, user_dto.last_name)

        print 'Testing user deletion ...'
        user_dao.delete(user_dto)

        assert_user = user_dao.find(id=user_dto.id)
        self.assertTrue(assert_user is None)

        print 'UserDAO tests passed'

    def test_merge_records(self):
        contact_dto = DTOConverter.to_dto(ContactDTO, self.contact)
        contact_dao = self.ctx.get_object("ContactDAO")

        print 'Saving initial record ...'
        contact_dao.create_update(contact_dto)

        print 'Creating a duplicate and attempting an insert ...'
        new_contact = Contact(email="jdegner0129@gmail.com",
                              phone=4029813230)
        new_contact_dto = DTOConverter.to_dto(ContactDTO, new_contact)
        contact_dao.create_update(new_contact_dto)

        print 'Asserting that the old contact was updated'
        assert_contact = contact_dao.find(id=contact_dto.id)
        self.assertEqual(assert_contact.phone, new_contact_dto.phone)

        print 'Merge records tests passed'

if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0]:
            raise