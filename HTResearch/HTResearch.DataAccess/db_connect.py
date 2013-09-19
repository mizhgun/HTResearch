from mongoengine import connect
from dto import ContactDTO
from dao import ContactDAO
from factory import DAOFactory

connect('researchData')

my_contact = ContactDTO()
my_contact.first_name = "Jordan"
my_contact.last_name = "Degner"
my_contact.email = "jdegner0129@gmail.com"

DAOFactory.GetInstance(ContactDAO).Create(my_contact)