import sys
import unittest
[sys.path.remove(p) for p in sys.path if 'DataAccess' in p]
sys.path.append('../DataAccess/')
from mongoengine.connection import connect, disconnect, get_connection
from dto import ContactDTO, OrganizationDTO, PublicationDTO
from dao import ContactDAO, OrganizationDAO, PublicationDAO
from factory import DAOFactory

class DatabaseInteractionTest(unittest.TestCase):

    mongodb_name = 'db_test'

    def setUp(self):
        print "New DatabaseInteractionTest running"
        disconnect()
        connect(self.mongodb_name)
        print 'Creating mongo test-database: ' + self.mongodb_name

    def tearDown(self):
        connection = get_connection()
        connection.drop_database(self.mongodb_name)
        print 'Dropping mongo test-database: ' + self.mongodb_name
        disconnect()

    def test_dao(self):
        my_contact = ContactDTO()
        my_contact.first_name = "Jordan"
        my_contact.last_name = "Degner"
        my_contact.email = "jdegner0129@gmail.com"
        DAOFactory.GetInstance(ContactDAO).Create(my_contact)
        assert_contact=DAOFactory.GetInstance(ContactDAO).Find(my_contact.id)
        self.assertTrue(assert_contact.first_name == "Jordan")
        self.assertTrue(assert_contact.last_name == "Degner")
        self.assertTrue(assert_contact.email == "jdegner0129@gmail.com")
        print 'ContactDAO tests passed'

        my_organization = OrganizationDTO()
        my_organization.name = "Yee University"
        my_organization.organization_url = "http://com.bee.yee"
        contacts = []
        contacts.append(my_contact)
        contacts.append(assert_contact)
        my_organization.contacts = contacts
        DAOFactory.GetInstance(OrganizationDAO).Create(my_organization)
        assert_organization=DAOFactory.GetInstance(OrganizationDAO).Find(my_organization.id)
        self.assertTrue(assert_organization.contacts == contacts)
        self.assertTrue(assert_organization.name == my_organization.name)
        self.assertTrue(assert_organization.organization_url == my_organization.organization_url)
        print 'OrganizationDAO tests passed'

        my_publication = PublicationDTO()
        my_publication.title = "The Book of Yee"
        my_publication.authors = contacts
        my_publication.publication_date = '2006-10-25 14:30:59'
        DAOFactory.GetInstance(PublicationDAO).Create(my_publication)
        assert_publication=DAOFactory.GetInstance(PublicationDAO).Find(my_publication.id)
        self.assertTrue(assert_publication.title == my_publication.title)
        self.assertTrue(assert_publication.authors == my_publication.authors)
        print 'PublicationDAO tests passed'

if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0]:
            raise
    print 'DB interaction test complete'