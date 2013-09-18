from mongoengine import *

class ContactDTO(Document):
    """A DTO wrapper for Contact documents"""

    first_name = StringField()
    last_name = StringField()
    primary_phone = IntField()
    secondary_phone = IntField()
    email = EmailField()
    organizations = ListField(ReferenceField('OrganizationDTO'))
    publications = ListField(ReferenceField('PublicationDTO'))
    position = StringField()

class OrganizationDTO(Document):
    """A DTO wrapper for Organization documents"""

    name = StringField()
    address = StringField()
    types = StringField()
    phone_number = IntField()
    email = EmailField()
    contacts = ListField(ReferenceField(ContactDTO))
    organization_url = URLField()
    partners = ListField(ReferenceField('self'))

class PublicationDTO(Document):
    """A DTO wrapper for Publication documents"""

    title = StringField()
    authors = ListField(ReferenceField(ContactDTO))
    publisher = ReferenceField(ContactDTO)
    publication_date = DateTimeField()
    types = StringField()
    content_url = URLField()