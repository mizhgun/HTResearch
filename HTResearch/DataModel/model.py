from datetime import datetime

class Contact(object):
    """A model class for an anti-trafficking contact."""

    def __init__(self, first_name = None, last_name = None,
                 primary_phone = None, secondary_phone = None,
                 email = None, organizations = [],
                 publications = [], position = None):
        self.first_name = first_name
        self.last_name = last_name
        self.primary_phone = primary_phone
        self.email = email
        self.organizations = organizations
        self.publications = publications
        self.position = position

class Organization(object):
    """A model class for an anti-trafficking organization."""

    def __init__(self, name = None, address = None,
                 types = [], phone_number = None,
                 email = None, contacts = [],
                 organization_url = None,
                 partners = []):
        self.name = name
        self.address = address
        self.types = types
        self.phone_number = phone_number
        self.email = email
        self.contacts = contacts
        self.organization_url = organization_url
        self.partners = partners

class Publication(object):
    """A model class for an anti-trafficking research publication."""

    def __init__(self, title = None, authors = [],
                 publisher = None, publication_date = datetime.now(),
                 types = [], content_url = None):
        self.title = title
        self.authors = authors
        self.publisher = publisher
        self.publication_date = publication_date
        self.types = types
        self.content_url = content_url

class URLMetadata(object):
    """A model class for an anti-trafficiking organization URL metadata."""

    def __init__(self, url = None, last_visited = datetime.now(),
                 score = None, update_freq = None,
                 checksum = None):
        self.url = url
        self.last_visited = last_visited
        self.score = score
        self.update_freq = update_freq
        self.checksum = checksum