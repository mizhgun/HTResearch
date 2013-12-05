import mongoengine as mongo
from HTResearch.DataModel.enums import AccountType, AffiliationType


class ContactDTO(mongo.Document):
    """A DTO wrapper for Contact documents"""

    first_name = mongo.StringField(db_field='f')
    last_name = mongo.StringField(db_field='l')
    phone = mongo.IntField(db_field='p1')
    email = mongo.EmailField(db_field='e')
    organization = mongo.ReferenceField('OrganizationDTO', db_field='o')
    publications = mongo.ListField(mongo.ReferenceField('PublicationDTO'), db_field='ps')
    position = mongo.StringField(db_field='pn')


class OrganizationDTO(mongo.Document):
    """A DTO wrapper for Organization documents"""

    name = mongo.StringField(db_field='n')
    address = mongo.StringField(db_field='a')
    latlng = mongo.ListField(db_field='l')
    types = mongo.ListField(mongo.IntField(), db_field='ts')
    phone_numbers = mongo.ListField(db_field='ns')
    email_key = mongo.EmailField(db_field='ek')
    emails = mongo.ListField(db_field='es')
    contacts = mongo.ListField(mongo.ReferenceField(ContactDTO), db_field='cs')
    organization_url = mongo.StringField(db_field='u')
    partners = mongo.ListField(mongo.ReferenceField('self'), db_field='ps')
    facebook = mongo.URLField(db_field='f')
    twitter = mongo.URLField(db_field='t')
    keywords = mongo.MapField(mongo.FloatField(), db_field='ks')


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
    domain = mongo.StringField(db_field='d')
    last_visited = mongo.DateTimeField(db_field='v')
    score = mongo.IntField(db_field='s')
    update_freq = mongo.IntField(db_field='f')
    checksum = mongo.BinaryField(db_field='c')


class UserDTO(mongo.Document):
    """A DTO wrapper for User documents"""

    first_name = mongo.StringField(db_field='f', max_length=80, required=True)
    last_name = mongo.StringField(db_field='l', max_length=80, required=True)
    email = mongo.EmailField(db_field='e', max_length=80, required=True)
    password = mongo.StringField(db_field='pa', min_length=8, max_length=80, required=True)
    background = mongo.StringField(db_field='b', required=True)
    account_type = mongo.IntField(db_field='at', required=True, choices=[AccountType.BASIC, AccountType.CONTRIBUTOR])
    affiliation = mongo.IntField(db_field='af', choices=[AffiliationType.STUDENT, AffiliationType.EMPLOYEE])
    organization = mongo.ReferenceField(OrganizationDTO, db_field='o')
