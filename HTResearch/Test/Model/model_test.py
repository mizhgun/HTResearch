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
        my_contact = model.Contact(first_name = "Jordan", last_name = "Degner")

        print 'Converting a contact to a DTO.'
        contact_dto = converter.DTOConverter.to_dto(dto.ContactDTO, my_contact)

        print 'Testing equality...'
        assert my_contact.first_name == contact_dto.first_name
        assert my_contact.last_name == contact_dto.last_name

        print 'Converting a DTO to a contact.'
        my_contact_again = converter.DTOConverter.from_dto(model.Contact, contact_dto)

        print 'Testing equality...'
        assert my_contact_again.first_name == contact_dto.first_name

if __name__ == '__main__':
    unittest.main()
    print 'Model testing complete.'