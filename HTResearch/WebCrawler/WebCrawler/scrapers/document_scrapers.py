from ..items import *
from utility_scrapers import *


class Contact:

    def __init__(self):
        contact = None


class OrganizationScraper():
    _scrapers = {
        'name': [OrgNameScraper()],
        'address': [OrgAddressScraper()],
        'types': [OrgTypeScraper()],
        'phone_number': [USPhoneNumberScraper(), IndianPhoneNumberScraper()],
        'email': [EmailScraper()],
        'contacts': [OrgContactsScraper()],
        'organization_url': [OrgUrlScraper()],
        'partners': [OrgPartnersScraper()],
    }

    _multiple = ['address', 'types', 'phone_number', 'email', 'contacts', 'partners', ]

    def parse(self, response):
        organization = ScrapedOrganization()
        # Collect each field of organization model
        for field in self._scrapers.iterkeys():
            if field in self._multiple:
                # Get multiple field (e.g. phone_number)
                organization[field] = []
                for scraper in self._scrapers[field]:
                    organization[field] += scraper.parse(response)
            else:
                # Get single field (e.g. name)
                results = self._scrapers[field][0].parse(response)
                organization[field] = results[0] if results else None
        return organization


class Publication:

    def __init__(self):
        publication = None