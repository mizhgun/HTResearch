import mongoengine as mongo

from HTResearch.DataModel.enums import AccountType
from HTResearch.DataModel.globals import ORG_TYPE_CHOICES


class ContactDTO(mongo.Document):
    """A DTO wrapper for Contact documents"""

    first_name = mongo.StringField(db_field='f')
    last_name = mongo.StringField(db_field='l')
    phones = mongo.ListField(db_field='p')
    email = mongo.EmailField(db_field='e')
    organization = mongo.ReferenceField('OrganizationDTO', db_field='o')
    publications = mongo.ListField(mongo.ReferenceField('PublicationDTO'), db_field='ps')
    position = mongo.StringField(db_field='pn')
    valid = mongo.BooleanField(db_field='v', default=True)
    last_updated = mongo.DateTimeField(db_field='lu')
    updated_by = mongo.ObjectIdField(db_field='ub')


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
    keywords = mongo.StringField(db_field='ks')
    valid = mongo.BooleanField(db_field='v', default=True)
    last_updated = mongo.DateTimeField(db_field='lu')
    updated_by = mongo.ObjectIdField(db_field='ub')
    references = mongo.ReferenceField(document_type=PageRankInfoDTO, db_field='r')


class PageRankInfoDTO(mongo.EmbeddedDocument):
    """A DTO wrapper for Information related to PageRank """

    total_with_self = mongo.LongField(min_value=0, max_value=None, db_field='ts')
    total = mongo.LongField(min_value=0, max_value=None, db_field='t')
    references = mongo.ListField(field=mongo.EmbeddedDocumentField(field=PageRankVectorDTO), db_field='r')


class PageRankVectorDTO(mongo.EmbeddedDocument):
    """A DTO wrapper for counting referenced organizations"""

    org_domain = mongo.StringField(db_field='o')
    count = mongo.LongField(min_value=0, max_value=None, db_field='c')
    pages = mongo.ListField(field=mongo.EmbeddedDocumentField(field=UrlCountPairDTO), db_field='p')


class PublicationDTO(mongo.Document):
    """A DTO wrapper for Publication documents"""

    title = mongo.StringField(db_field='t')
    authors = mongo.StringField(db_field='as')
    publisher = mongo.StringField(db_field='p')
    publication_date = mongo.DateTimeField(db_field='d')
    types = mongo.ListField(mongo.IntField(), db_field='ts')
    content_url = mongo.URLField(db_field='u')
    valid = mongo.BooleanField(db_field='v', default=True)
    last_updated = mongo.DateTimeField(db_field='lu')
    updated_by = mongo.ObjectIdField(db_field='ub')


class UrlCountPairDTO(mongo.EmbeddedDocument):
    """A DTO wrapper for pairing Source URLs and the Number of References to some Page"""

    url = mongo.URLField(db_field='u')
    count = mongo.LongField(min_value=0, max_value=None, db_field='c')


class URLMetadataDTO(mongo.Document):
    """A DTO wrapper for URLMetadata documents"""

    url = mongo.URLField(db_field='u')
    domain = mongo.StringField(db_field='d')
    last_visited = mongo.DateTimeField(db_field='v')
    score = mongo.IntField(db_field='s')
    update_freq = mongo.IntField(db_field='f')
    checksum = mongo.BinaryField(db_field='c')
    last_updated = mongo.DateTimeField(db_field='lu')


class UserDTO(mongo.Document):
    """A DTO wrapper for User documents"""

    first_name = mongo.StringField(db_field='f', max_length=25, required=True)
    last_name = mongo.StringField(db_field='l', max_length=25, required=True)
    email = mongo.EmailField(db_field='e', max_length=40, required=True)
    password = mongo.StringField(db_field='pa', required=True)
    background = mongo.StringField(db_field='b', max_length=120, required=True)
    account_type = mongo.IntField(db_field='at', required=True,
                                  choices=(AccountType.COLLABORATOR, AccountType.CONTRIBUTOR))
    org_type = mongo.IntField(db_field='ot', choices=ORG_TYPE_CHOICES)
    organization = mongo.ReferenceField(OrganizationDTO, db_field='o')
    last_updated = mongo.DateTimeField(db_field='lu')
