import mongoengine as Mongo


class ContactDTO(Mongo.Document):
    """A DTO wrapper for Contact documents"""

    first_name = Mongo.StringField(db_field='f')
    last_name = Mongo.StringField(db_field='l')
    primary_phone = Mongo.IntField(db_field='p1')
    secondary_phone = Mongo.IntField(db_field='p2')
    email = Mongo.EmailField(db_field='e')
    organizations = Mongo.ListField(Mongo.ReferenceField('OrganizationDTO'), db_field='os')
    publications = Mongo.ListField(Mongo.ReferenceField('PublicationDTO'), db_field='ps')
    position = Mongo.StringField(db_field='pn')


class OrganizationDTO(Mongo.Document):
    """A DTO wrapper for Organization documents"""

    name = Mongo.StringField(db_field='n')
    address = Mongo.StringField(db_field='a')
    types = Mongo.ListField(Mongo.IntField(), db_field='ts')
    phone_number = Mongo.IntField(db_field='p')
    email = Mongo.EmailField(db_field='e')
    contacts = Mongo.ListField(Mongo.ReferenceField(ContactDTO), db_field='cs')
    organization_url = Mongo.URLField(db_field='u')
    partners = Mongo.ListField(Mongo.ReferenceField('self'), db_field='ps')


class PublicationDTO(Mongo.Document):
    """A DTO wrapper for Publication documents"""

    title = Mongo.StringField(db_field='t')
    authors = Mongo.ListField(Mongo.ReferenceField(ContactDTO), db_field='as')
    publisher = Mongo.ReferenceField(ContactDTO, db_field='p')
    publication_date = Mongo.DateTimeField(db_field='d')
    types = Mongo.ListField(Mongo.IntField(), db_field='ts')
    content_url = Mongo.URLField(db_field='u')


class URLMetadataDTO(Mongo.Document):
    """A DTO wrapper for URLMetadata documents"""

    url = Mongo.URLField(db_field='u')
    last_visited = Mongo.DateTimeField(db_field='v')
    score = Mongo.IntField(db_field='s')
    update_freq = Mongo.IntField(db_field='f')
    checksum = Mongo.IntField(db_field='c')