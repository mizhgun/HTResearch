import unittest

from htresearch.dataaccess.dto import ContactDTO
from htresearch.datamodel.converter import DTOConverter
from htresearch.datamodel.model import Contact


class ModelTest(unittest.TestCase):
    def test_converter(self):
        my_contact = Contact(first_name = "Jordan",
                                   last_name = "Degner",
                                   primary_phone = 4029813230,
                                   email = "jdegner0129@gmail.com",
                                   position = "Software Engineer")

        print 'Converting a contact to a DTO.'
        contact_dto = DTOConverter.to_dto(ContactDTO, my_contact)

        print 'Testing equality...'
        for attr, value in my_contact.__dict__.iteritems():
            self.assertEqual(getattr(my_contact, attr), getattr(contact_dto, attr), "{0} attribute not equal".format(attr))

        print 'Converting a DTO to a contact.'
        my_contact = DTOConverter.from_dto(Contact, contact_dto)

        print 'Testing equality...'
        for attr, value in my_contact.__dict__.iteritems():
            self.assertEqual(getattr(my_contact, attr), getattr(contact_dto, attr), "{0} attribute not equal".format(attr))

if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0]:
            raise