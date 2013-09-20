import mongoengine as Mongo

class ContactDTO(Document):
    """A DTO wrapper for Contact documents"""

    first_name = Mongo.StringField()
    last_name = Mongo.StringField()
    primary_phone = Mongo.IntField()
    secondary_phone = Mongo.IntField()
    email = Mongo.EmailField()
    organizations = Mongo.ListField(ReferenceField('OrganizationDTO'))
    publications = Mongo.ListField(ReferenceField('PublicationDTO'))
    position = Mongo.StringField()

class OrganizationDTO(Document):
    """A DTO wrapper for Organization documents"""

    name = Mongo.StringField()
    address = Mongo.StringField()
    types = Mongo.StringField()
    phone_number = Mongo.IntField()
    email = Mongo.EmailField()
    contacts = Mongo.ListField(ReferenceField(ContactDTO))
    organization_url = Mongo.URLField()
    partners = Mongo.ListField(ReferenceField('self'))

class PublicationDTO(Document):
    """A DTO wrapper for Publication documents"""

    title = Mongo.StringField()
    authors = Mongo.ListField(ReferenceField(ContactDTO))
    publisher = Mongo.ReferenceField(ContactDTO)
    publication_date = Mongo.DateTimeField()
    types = Mongo.StringField()
    content_url = Mongo.URLField()