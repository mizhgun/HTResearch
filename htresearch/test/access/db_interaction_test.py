import unittest

from HTResearch.DataAccess.dto import *
from HTResearch.DataAccess.dao import *
from HTResearch.DataAccess.connection import DBConnection
from HTResearch.DataAccess.factory import DAOFactory
from HTResearch.DataModel.model import *
from HTResearch.DataModel.converter import DTOConverter


class DatabaseInteractionTest(unittest.TestCase):

    mongodb_name = 'db_test'

    def setUp(self):
        print "New DatabaseInteractionTest running"

        self.contact = Contact(first_name = "Jordan", 
                               last_name = "Degner",
                               email = "jdegner0129@gmail.com")
        self.organization = Organization(name = "Yee University", 
                                         organization_url = "http://com.bee.yee", 
                                         contacts = [self.contact])
        self.publication = Publication(title = "The Book of Yee", 
                                       authors = [self.contact])
        self.urlmetadata = URLMetadata(url = "http://google.com")

    def tearDown(self):
        with DBConnection() as c:
            c.dropall()

    def test_contact_dao(self):
        contact_dto = DTOConverter.to_dto(ContactDTO, self.contact)
        contact_dao = DAOFactory.get_instance(ContactDAO)

        print 'Testing contact creation ...'
        contact_dao.create_update(contact_dto)
        
        assert_contact = contact_dao.find(contact_dto.id)
        self.assertEqual(assert_contact.first_name, contact_dto.first_name)
        self.assertEqual(assert_contact.last_name, contact_dto.last_name)
        self.assertEqual(assert_contact.email, contact_dto.email)

        print 'Testing contact editing ...'
        contact_dto.first_name = "Djordan"
        contact_dao.create_update(contact_dto)

        assert_contact = contact_dao.find(contact_dto.id)
        self.assertEqual(assert_contact.first_name, contact_dto.first_name)

        print 'Testing contact deletion ...'
        contact_dao.delete(contact_dto)

        assert_contact = contact_dao.find(contact_dto.id)
        self.assertTrue(assert_contact is None)

        print 'ContactDAO tests passed'

    def test_organization_dao(self):
        org_dto = DTOConverter.to_dto(OrganizationDTO, self.organization)
        org_dao = DAOFactory.get_instance(OrganizationDAO)

        print 'Testing organization creation ...'
        org_dao.create_update(org_dto)

        assert_org = org_dao.find(org_dto.id)
        self.assertEqual(assert_org.name, org_dto.name)
        self.assertEqual(assert_org.organization_url, org_dto.organization_url)
        self.assertEqual(assert_org.contacts, org_dto.contacts)

        print 'Testing organization editing ...'
        org_dto.name = "Yee Universityee"
        org_dto.contacts = []
        org_dao.create_update(org_dto)

        assert_org = org_dao.find(org_dto.id)
        self.assertEqual(assert_org.name, org_dto.name)
        self.assertEqual(assert_org.organization_url, org_dto.organization_url)
        self.assertEqual(assert_org.contacts, org_dto.contacts)

        print 'Testing organization deletion ...'
        org_dao.delete(org_dto)

        assert_org = org_dao.find(org_dto.id)
        self.assertTrue(assert_org is None)

        print 'OrganizationDAO tests passed'

    def test_publication_dao(self):
        pub_dto = DTOConverter.to_dto(PublicationDTO, self.publication)
        pub_dao = DAOFactory.get_instance(PublicationDAO)

        print 'Testing publication creation ...'
        pub_dao.create_update(pub_dto)

        assert_pub = pub_dao.find(pub_dto.id)
        self.assertEqual(assert_pub.title, pub_dto.title)
        self.assertEqual(assert_pub.authors, pub_dto.authors)

        print 'Testing publication editing ...'
        pub_dto.title = "The Book of Mee"
        pub_dao.create_update(pub_dto)

        assert_pub = pub_dao.find(pub_dto.id)
        self.assertEqual(assert_pub.title, pub_dto.title)

        print 'Testing publication deletion ...'
        pub_dao.delete(pub_dto)

        assert_pub = pub_dao.find(pub_dto.id)
        self.assertTrue(assert_pub is None)

        print 'PublicationDAO tests passed'

    def test_urlmetadata_dao(self):
        url_dto = DTOConverter.to_dto(URLMetadataDTO, self.urlmetadata)
        url_dao = DAOFactory.get_instance(URLMetadataDAO)

        print 'Testing URL creation ...'
        url_dao.create_update(url_dto)

        assert_url = url_dao.find(url_dto.id)
        self.assertEqual(assert_url.url, url_dto.url)
        
        print 'Testing URL editing ...'
        url_dto.url = "http://facebook.com"
        url_dao.create_update(url_dto)

        assert_url = url_dao.find(url_dto.id)
        self.assertEqual(assert_url.url, url_dto.url)

        print 'Testing URL deletion ...'
        url_dao.delete(url_dto)

        assert_url = url_dao.find(url_dto.id)
        self.assertTrue(assert_url is None)

        print 'URLMetadataDAO tests passed'

if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0]:
            raise