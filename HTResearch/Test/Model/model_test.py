# stdlib imports
import unittest
from springpython.context import ApplicationContext
from springpython.config import Object

# project imports
from HTResearch.DataAccess.dto import ContactDTO, OrganizationDTO
from HTResearch.Utilities.converter import DTOConverter
from HTResearch.DataModel.model import Contact, Organization
from HTResearch.Utilities.context import ConverterContext
from HTResearch.Test.Mocks.dao import MockOrganizationDAO
from HTResearch.WebCrawler.WebCrawler.items import ScrapedContact

class TestableDAOContext(ConverterContext):

    @Object()
    def RegisteredOrganizationDAO(self):
        return MockOrganizationDAO

class ModelTest(unittest.TestCase):

    def test_dto_converter(self):
        my_contact = Contact(first_name="Jordan",
                             last_name="Degner",
                             phone=4029813230,
                             email="jdegner0129@gmail.com",
                             position="Software Engineer",
                             )


        print 'Converting a contact to a DTO.'
        contact_dto = DTOConverter.to_dto(ContactDTO, my_contact)

        print 'Testing equality...'
        for attr, value in my_contact.__dict__.iteritems():
            self.assertEqual(getattr(my_contact, attr), getattr(contact_dto, attr),
                             "{0} attribute not equal".format(attr))


        print 'Converting a DTO to a contact.'
        my_contact = DTOConverter.from_dto(Contact, contact_dto)

        print 'Testing equality...'
        for attr, value in my_contact.__dict__.iteritems():
            self.assertEqual(getattr(my_contact, attr), getattr(contact_dto, attr),
                             "{0} attribute not equal".format(attr))

    def test_item_converter(self):
        print 'Creating organization and contact item.'
        org = MockOrganizationDAO()
        org_dto = OrganizationDTO(name="Univerisityee of Nyeebraska-Lincoln")
        org.create_update(org_dto)
        org_model = DTOConverter.from_dto(Organization, org_dto)
        contact_item = ScrapedContact(first_name='Bee',
                                      last_name='Yee',
                                      organization={'name': "Univerisityee of Nyeebraska-Lincoln"}
                                      )

        print 'Converting contact to model.'
        ctx = ApplicationContext(TestableDAOContext())
        converter = ctx.get_object('ModelConverter')
        model_contact = converter.to_model(Contact, contact_item)

        self.assertEqual(model_contact.organization.name, org_model.name)








if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0]:
            raise