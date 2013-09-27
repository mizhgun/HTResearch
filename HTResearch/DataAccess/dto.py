import mongoengine as Mongo

class ContactDTO(Mongo.Document):
    """A DTO wrapper for Contact documents"""

    first_name = Mongo.StringField()
    last_name = Mongo.StringField()
    primary_phone = Mongo.IntField()
    secondary_phone = Mongo.IntField()
    email = Mongo.EmailField()
    organizations = Mongo.ListField(Mongo.ReferenceField('OrganizationDTO'))
    publications = Mongo.ListField(Mongo.ReferenceField('PublicationDTO'))
    position = Mongo.StringField()

class OrganizationDTO(Mongo.Document):
    """A DTO wrapper for Organization documents"""

    name = Mongo.StringField()
    address = Mongo.StringField()
    types = Mongo.ListField(Mongo.IntField())
    phone_number = Mongo.IntField()
    email = Mongo.EmailField()
    contacts = Mongo.ListField(Mongo.ReferenceField(ContactDTO))
    organization_url = Mongo.URLField()
    partners = Mongo.ListField(Mongo.ReferenceField('self'))

class PublicationDTO(Mongo.Document):
    """A DTO wrapper for Publication documents"""

    title = Mongo.StringField()
    authors = Mongo.ListField(Mongo.ReferenceField(ContactDTO))
    publisher = Mongo.ReferenceField(ContactDTO)
    publication_date = Mongo.DateTimeField()
    types = Mongo.ListField(Mongo.IntField())
    content_url = Mongo.URLField()

class URLMetadataDTO(Mongo.Document):
    """A DTO wrapper for URLMetadata documents"""

    url = Mongo.URLField()
    last_visited = Mongo.DateTimeField()
    score = Mongo.IntegerField()
    update_freq = Mongo.IntegerField()
    checksum = Mongo.IntegerField()