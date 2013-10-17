from ..items import *
from utility_scrapers import *

class Contact:

    def __init__(self):
        contact = None

class OrganizationScraper:
    _scrapers = {
        'name': [],
        'address': [OrgAddressScraper()],
        'types': [OrgTypeScraper()],
        'phone_number': [USPhoneNumberScraper(), IndianPhoneNumberScraper()],
        'email': [EmailScraper()],
        'contacts': [],
        'organization_url': [],
        'partners': [],
    }

    def parse(self, response):
        organization = ScrapedOrganization()
        for field in self._scrapers.iterkeys():
            organization[field] = []
            for scraper in self._scrapers[field]:
                organization[field] += scraper.parse(response)
        return organization


class Publication:

    def __init__(self):
        publication = None