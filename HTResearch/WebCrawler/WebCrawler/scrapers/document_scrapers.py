from ..items import *
from utility_scrapers import *
import string
import re


class Contact:

    def __init__(self):
        contact = None


class OrganizationScraper():
    def __init__(self):
        self._required_words = ['prostitution', 'sex trafficking', 'child labor', 'child labour', 'slavery',
                                'human trafficking', 'brothel', 'child trafficking', 'anti trafficking']
        self._punctuation = re.compile('[%s]' % re.escape(string.punctuation))

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

    _multiple = ['types', 'phone_number', 'email', 'contacts', 'partners', ]

    def parse(self, response):
        organization = ScrapedOrganization()

        flag = self.check_valid_org(response)
        if flag:
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
                    if results:
                        organization[field] = results[0] if isinstance(results, type([])) else results
                    else:
                        organization[field] = None
        return organization

    def check_valid_org(self, response):
        hxs = HtmlXPathSelector(response)
        site_text = hxs.select('//html//text()').extract()
        site_text = [element.strip() for element in site_text if element.strip() != '']

        for word in self._required_words:
            for sentence in site_text:
                sentence = self._punctuation.sub(' ', sentence)
                if word in sentence.lower():
                    return True
        return False


class Publication:

    def __init__(self):
        publication = None