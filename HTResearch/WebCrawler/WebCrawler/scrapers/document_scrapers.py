from ..items import *
from utility_scrapers import *
import string
import re
from HTResearch.Utilities.url_tools import UrlUtility
from HTResearch.DataModel.model import URLMetadata
from HTResearch.URLFrontier.urlfrontier import URLFrontier


class ContactScraper():

    def __init__(self):
        contact = None


class OrganizationScraper():
    def __init__(self):
        self._scrapers = {
            'name': [OrgNameScraper],
            'address': [OrgAddressScraper],
            'types': [OrgTypeScraper],
            'phone_numbers': [USPhoneNumberScraper, IndianPhoneNumberScraper],
            'emails': [EmailScraper],
            'contacts': [OrgContactsScraper],
            'organization_url': [OrgUrlScraper],
            'partners': [OrgPartnersScraper],
            'facebook': [OrgFacebookScraper],
        }
        self._multiple = ['types', 'phone_numbers', 'emails', 'contacts', 'partners', ]
        self._required_words = ['prostitution', 'sex trafficking', 'child labor', 'child labour', 'slavery',
                                'human trafficking', 'brothel', 'child trafficking', 'anti trafficking',
                                'social justice']
        self._punctuation = re.compile('[%s]' % re.escape(string.punctuation))
        self.org_dao = OrganizationDAO
        self.url_frontier = URLFrontier()

    def parse(self, response):
        organization = None

        flag = self.check_valid_org(response)
        if flag:
            organization = ScrapedOrganization()
            # Collect each field of organization model
            for field in self._scrapers.iterkeys():
                if field in self._multiple:
                    # Get multiple field (e.g. phone_number)
                    organization[field] = []
                    for scraper in self._scrapers[field]:
                        organization[field] += scraper().parse(response)
                else:
                    # Get single field (e.g. name)
                    results = (self._scrapers[field][0])().parse(response)
                    if results:
                        organization[field] = results[0] if isinstance(results, type([])) else results
                    else:
                        organization[field] = None
        return organization

    def check_valid_org(self, response):
        # If already in database, then valid
        url = OrgUrlScraper().parse(response)
        org_dto = self.org_dao().find(organization_url=url)
        if org_dto:
            return True

        # If not homepage, then return false and make sure homepage is added to scrape:
        home_url_obj = urlparse(response.request.url)
        if home_url_obj.path and home_url_obj.path is not '/':
            home_url = home_url_obj.scheme + '://' + home_url_obj.netloc + '/'
            home_domain = UrlUtility.get_domain(home_url)
            meta = URLMetadata(url=home_url, domain=home_domain, last_visited=datetime(1, 1, 1))
            self.url_frontier.put_url(meta)
            return False
        else:
            # this is homepage, scrape for keywords
            hxs = HtmlXPathSelector(response)
            site_text = hxs.select('//html//text()').extract()
            site_text = [element.strip() for element in site_text if element.strip() != '']

            for word in self._required_words:
                for sentence in site_text:
                    sentence = self._punctuation.sub(' ', sentence)
                    if word in sentence.lower():
                        return True
            # no keyword found, check if we already added organization

        return False


class PublicationScraper():

    def __init__(self):
        publication = None