#
# model.py
# A module for the data models corresponding to important anti-trafficking information.
#


from datetime import datetime


class Contact(object):
    """A Model class for an anti-trafficking contact."""

    def __init__(self, first_name=None, last_name=None,
                 phones=[], email=None, organization=None,
                 publications=[], position=None, valid=True,
                 updated_by=None, content_weight=None):
        """
        Constructs a new Contact instance.

        Arguments:
            first_name (string): The contact's first name.
            last_name (string): The contact's last name.
            phones (string[]): The contact's phone numbers.
            email (string): The contact's email.
            organization (Organization): The contact's affiliated organization.
            publications (Publication[]): The contact's publications.
            valid (boolean): The validity of the contact.
            last_updated (DateTime): The date the contact was last updated.
            updated_by (ObjectId): The user that last updated the contact.
            content_weight (float): The weight of the contact's content.
        """
        self.first_name = first_name
        self.last_name = last_name
        self.phones = phones
        self.email = email
        self.organization = organization
        self.publications = publications
        self.position = position
        self.valid = valid
        self.last_updated = datetime.utcnow()
        self.updated_by = updated_by
        self.content_weight = content_weight


class Organization(object):
    """A Model class for an anti-trafficking organization."""

    def __init__(self, name=None, address=None,
                 types=[], phone_numbers=[], email_key=None,
                 emails=[], contacts=[],
                 organization_url=None,
                 partners=[], facebook=None, twitter=None,
                 keywords=None, valid=True, updated_by=None,
                 page_rank_info=None, page_rank=None, page_rank_weight=None,
                 content_weight=None, combined_weight=None):
        """
        Constructs a new Organization instance.

        Arguments:
            name (string): The name of the organization.
            address (string): The address of the organization.
            types (OrgTypeEnum[]): The types of the organization.
            phone_numbers (string[]): The phone numbers for the organization.
            email_key (string): The primary email for the organization.
            emails (string[]): The emails for the organization.
            contacts (Contact[]): The contacts for the organization.
            organization_url (string): The URL for the organization's website.
            partners (Organization[]): The partner organizations.
            facebook (string): The Facebook URL for the organization.
            twitter (string): The Twitter URL for the organization.
            keywords (string[]): The list of keywords.
            valid: Whether or not the organization is valid.
            updated_by (ObjectId): The object id of the last user to update the organization.
            page_rank_info (PageRankInfo): The organization's PageRank information.
            page_rank (int): The PageRank value for the organization.
            page_rank_weight (float): A weight from 0 - 1 for the organization's Page Rank.
            content_weight (float): A weight from 0 - 1 for the organization's content.
            combined_weight (float): The combined weight of content and PageRank.
        """
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
        self.page_rank_info = page_rank_info
        self.page_rank = page_rank
        self.page_rank_weight = page_rank_weight
        self.content_weight = content_weight
        self.combined_weight = combined_weight


class PageRankInfo(object):
    """A Model class for Information related to PageRank """

    def __init__(self, total_with_self=0, total=0,
                 references=[]):
        """
        Constructs a new PageRankInfo instance.

        Arguments:
            TODO: put arguments here
        """
        self.total_with_self = total_with_self
        self.total = total
        self.references = references


class PageRankVector(object):
    """A Model class for counting referenced organizations"""

    def __init__(self, org_domain=None, count=0,
                 pages=[]):
        """
        Constructs a new PageRankVector instance.

        Arguments:
            TODO: put arguments here
        """
        self.org_domain = org_domain
        self.count = count
        self.pages = pages


class Publication(object):
    """A Model class for an anti-trafficking research publication."""

    def __init__(self, title=None, authors=None,
                 publisher=None, publication_date=datetime.utcnow(),
                 types=[], content_url=None, valid=True,
                 updated_by=None):
        """
        Constructs a new Publication instance.

        Arguments:
            title (string): The publication title.
            authors (Contact[]): The list of authors.
            publisher (string): The publisher of the publication.
            publication_date (DateTime): The date of publication.
            types (OrgTypeEnum[]): The types associated with the publication.
            content_url (string): The URL for the publication.
            valid (boolean): The validity of the publication.
            updated_by (ObjectId): The object id of the publication's last updater.
        """
        self.title = title
        self.authors = authors
        self.publisher = publisher
        self.publication_date = publication_date
        self.types = types
        self.content_url = content_url
        self.valid = valid
        self.last_updated = datetime.utcnow()
        self.updated_by = updated_by


class UrlCountPair(object):
    """A Model class for pairing source URLs and the number of references to some page."""

    def __init__(self, url=None, count=0):
        """
        Constructs a new UrlCountPair object.

        Arguments:
            url (string): The URL for this pairing.
            count (int): The number of instances of this URL.
        """
        self.url = url
        self.count = count


class URLMetadata(object):
    """A Model class for an anti-trafficiking organization URL metadata."""

    def __init__(self, url=None, domain=None, last_visited=datetime.utcnow(),
                 score=None, update_freq=None,
                 checksum=None):
        """
        Constructs a new URLMetadata object.

        Arguments:
            url (string): The URL this metadata is for.
            domain (string): The domain for the URL.
            last_visited (DateTime): The last visitation date for this URL.
            score (int): The score for this URL.
            update_freq (long): The frequency of updates to this page.
            checksum (string): The checksum for the URL's content.
        """
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
                 organization=None, content_weight=None):
        """
        Constructs a new User object.

        Arguments:
            first_name (string): The user's first name.
            last_name (string): The user's last name.
            email (string): The user's email.
            password (string): The user's password.
            background (string): The user's professional background.
            account_type (AccountType): The user's account type.
            org_type (OrgTypeEnum): The user's organization type.
            organization (Organization): The user's affiliated organization.
            content_weight (float): The 0 - 1 ranking of the user content.
        """
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.background = background
        self.account_type = account_type
        self.org_type = org_type
        self.organization = organization
        self.last_updated = datetime.utcnow()
        self.content_weight = content_weight
