import unittest
import sys

modules = ['DataAccess', 'DataModel']
for m in modules:
    [sys.path.remove(p) for p in sys.path if m in p]

[sys.path.append('../' + m) for m in modules]

import dto
import converter
import model

class ModelTest(unittest.TestCase):
    def test_converter(self):
        my_contact = model.Contact(first_name = "Jordan", 
                                   last_name = "Degner",
                                   primary_phone = 4029813230,
                                   secondary_phone = None,
                                   email = "jdegner0129@gmail.com",
                                   position = "Software Engineer")

        print 'Converting a contact to a DTO.'
        contact_dto = converter.DTOConverter.to_dto(dto.ContactDTO, my_contact)

        print 'Testing equality...'
        for attr, value in my_contact.__dict__.iteritems():
            self.assertEqual(getattr(my_contact, attr), getattr(contact_dto, attr), "{0} attribute not equal".format(attr))

        print 'Converting a DTO to a contact.'
        my_contact = converter.DTOConverter.from_dto(model.Contact, contact_dto)

        print 'Testing equality...'
        for attr, value in my_contact.__dict__.iteritems():
            self.assertEqual(getattr(my_contact, attr), getattr(contact_dto, attr), "{0} attribute not equal".format(attr))

if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0]:
            raise