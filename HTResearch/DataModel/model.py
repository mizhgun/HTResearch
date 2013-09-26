from datetime import datetime

class Contact(object):
    """A model class for an anti-trafficking contact."""

    def __init__(self, first_name = "", last_name = "",
                 primary_phone = 0, secondary_phone = 0,
                 email = "", organizations = [],
                 publications = [], position = ""):
        self.first_name = first_name
        self.last_name = last_name
        self.primary_phone = primary_phone
        self.email = email
        self.organizations = organizations
        self.publications = publications
        self.position = position

class Organization(object):
    """A model class for an anti-trafficking organization."""

    def __init__(self, name = "", address = "",
                 types = [], phone_number = 0,
                 email = "", contacts = [],
                 organization_url = "",
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

    def __init__(self, title = "", authors = [],
                 publisher = None, publication_date = datetime.now(),
                 types = [], content_url = ""):
        self.title = title
        self.authors = authors
        self.publisher = publisher
        self.publication_date = publication_date
        self.types = types
        self.content_url = content_url