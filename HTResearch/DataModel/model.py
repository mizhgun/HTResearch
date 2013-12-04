from datetime import datetime


class Contact(object):
    """A Model class for an anti-trafficking contact."""

    def __init__(self, first_name=None, last_name=None,
                 phone=None, email=None, organization=None,
                 publications=[], position=None):
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.email = email
        self.organization = organization
        self.publications = publications
        self.position = position


class Organization(object):
    """A Model class for an anti-trafficking organization."""

    def __init__(self, name=None, address=None,
                 types=[], phone_numbers=[], email_key=None,
                 emails=[], contacts=[],
                 organization_url=None,
                 partners=[], facebook=None, twitter=None):
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


class Publication(object):
    """A Model class for an anti-trafficking research publication."""

    def __init__(self, title=None, authors=[],
                 publisher=None, publication_date=datetime.now(),
                 types=[], content_url=None):
        self.title = title
        self.authors = authors
        self.publisher = publisher
        self.publication_date = publication_date
        self.types = types
        self.content_url = content_url


class URLMetadata(object):
    """A Model class for an anti-trafficiking organization URL metadata."""

    def __init__(self, url=None, domain=None, last_visited=datetime.now(),
                 score=None, update_freq=None,
                 checksum=None):
        self.url = url
        self.domain = domain
        self.last_visited = last_visited
        self.score = score
        self.update_freq = update_freq
        self.checksum = checksum


class User(object):
    """A Model class for a user of the anti-trafficking system."""

    def __init__(self, first_name, last_name, email, phone, organization, position, interests=None, address=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.organization = organization
        self.position = position
        self.interests = interests
        self.address = address
