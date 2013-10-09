from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
from ..items import *
from utility_scrapers import *
import pdb
import re

class Contact:

    def __init__(self):
        contact = None

class Organization:
    _scrapers = {
        'name': OrgNameScraper(),
        'address': OrgAddressScraper(),
        'types': OrgTypeScraper(),
        'phone_number': USPhoneNumberScraper(),
        'email': EmailScraper(),
        'contacts': OrgContactsScraper(),
        'organization_url': OrgUrlScraper(),
        'partners': OrgPartnersScraper(),
    }

    def parse(self, response):
        organization = ScrapedOrganization()
        for field in self._scrapers.iterkeys():
            organization[field] = self._scrapers[field].parse(response)
        return organization

class Publication:

    def __init__(self):
        publication = None