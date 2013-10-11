import mongoengine as mongo


class ContactDTO(mongo.Document):
    """A DTO wrapper for Contact documents"""

    first_name = mongo.StringField(db_field='f')
    last_name = mongo.StringField(db_field='l')
    primary_phone = mongo.IntField(db_field='p1')
    secondary_phone = mongo.IntField(db_field='p2')
    email = mongo.EmailField(db_field='e')
    organizations = mongo.ListField(mongo.ReferenceField('OrganizationDTO'), db_field='os')
    publications = mongo.ListField(mongo.ReferenceField('PublicationDTO'), db_field='ps')
    position = mongo.StringField(db_field='pn')


class OrganizationDTO(mongo.Document):
    """A DTO wrapper for Organization documents"""

    name = mongo.StringField(db_field='n')
    address = mongo.StringField(db_field='a')
    types = mongo.ListField(mongo.IntField(), db_field='ts')
    phone_number = mongo.IntField(db_field='p')
    email = mongo.EmailField(db_field='e')
    contacts = mongo.ListField(mongo.ReferenceField(ContactDTO), db_field='cs')
    organization_url = mongo.URLField(db_field='u')
    partners = mongo.ListField(mongo.ReferenceField('self'), db_field='ps')


class PublicationDTO(mongo.Document):
    """A DTO wrapper for Publication documents"""

    title = mongo.StringField(db_field='t')
    authors = mongo.ListField(mongo.ReferenceField(ContactDTO), db_field='as')
    publisher = mongo.ReferenceField(ContactDTO, db_field='p')
    publication_date = mongo.DateTimeField(db_field='d')
    types = mongo.ListField(mongo.IntField(), db_field='ts')
    content_url = mongo.URLField(db_field='u')


class URLMetadataDTO(mongo.Document):
    """A DTO wrapper for URLMetadata documents"""

    url = mongo.URLField(db_field='u')
    last_visited = mongo.DateTimeField(db_field='v')
    score = mongo.IntField(db_field='s')
    update_freq = mongo.IntField(db_field='f')
    checksum = mongo.IntField(db_field='c')