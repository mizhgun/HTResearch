from datetime import datetime


class Contact(object):
    """A Model class for an anti-trafficking contact."""

    def __init__(self, first_name=None, last_name=None,
                 phone=None, email=None, organization=None,
                 publications=[], position=None, valid=True,
                 updated_by=None):
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.email = email
        self.organization = organization
        self.publications = publications
        self.position = position
        self.valid = valid
        self.last_updated = datetime.utcnow()
        self.updated_by = updated_by


class Organization(object):
    """A Model class for an anti-trafficking organization."""

    def __init__(self, name=None, address=None,
                 types=[], phone_numbers=[], email_key=None,
                 emails=[], contacts=[],
                 organization_url=None,
                 partners=[], facebook=None, twitter=None,
                 keywords={}, valid=True, updated_by=None):
        self.name = name
        self.address = address
        self.types = types
        self.phone_numbers = phone_numbers
        self.email_key = email_key
        self.emails = emails
        self.contacts = contacts
        self.organization_url = organization_url
        self.partners = partners
        self.facebook = facebook
        self.twitter = twitter
        self.keywords = keywords
        self.valid = valid
        self.last_updated = datetime.utcnow()
        self.updated_by = updated_by


class Publication(object):
    """A Model class for an anti-trafficking research publication."""

    def __init__(self, title=None, authors=[],
                 publisher=None, publication_date=datetime.utcnow(),
                 types=[], content_url=None, valid=True,
                 updated_by=None):
        self.title = title
        self.authors = authors
        self.publisher = publisher
        self.publication_date = publication_date
        self.types = types
        self.content_url = content_url
        self.valid = valid
        self.last_updated = datetime.utcnow()
        self.updated_by = updated_by


class URLMetadata(object):
    """A Model class for an anti-trafficiking organization URL metadata."""

    def __init__(self, url=None, domain=None, last_visited=datetime.utcnow(),
                 score=None, update_freq=None,
                 checksum=None):
        self.url = url
        self.domain = domain
        self.last_visited = last_visited
        self.score = score
        self.update_freq = update_freq
        self.checksum = checksum
        self.last_updated = datetime.utcnow()


class User(object):
    """A Model class for a user of the anti-trafficking system."""

    def __init__(self, first_name=None, last_name=None,
                 email=None, password=None, background=None,
                 account_type=None, org_type=None,
                 organization=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.background = background
        self.account_type = account_type
        self.org_type = org_type
        self.organization = organization
