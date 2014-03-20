#
# document_scrapers.py
# A module containing the document scrapers that are used to scrape data.
#

# stdlib imports
import re
import string

# project imports
from HTResearch.Utilities.url_tools import UrlUtility
from HTResearch.DataModel.model import URLMetadata
from HTResearch.URLFrontier.urlfrontier import URLFrontier
from link_scraper import PageRankScraper
from utility_scrapers import *


class ContactScraper():
    """A class that uses the OrgContactsScraper to find contacts associated with a particular organization."""
    def parse(self, response):
        #get all the values out of the dictionary that the Contact scraper returns
        org_contact_scraper = OrgContactsScraper()
        contact_dicts = org_contact_scraper.parse(response)
        contacts = []
        for name in contact_dicts.iterkeys():
            contact = ScrapedContact()
            name_split = name.split()
            n = len(name_split)
            contact['first_name'] = ' '.join(name_split[0:n - 1])
            contact['last_name'] = name_split[n - 1]
            contact['phones'] = contact_dicts[name]['number']
            contact['email'] = contact_dicts[name]['email']
            contact['position'] = contact_dicts[name]['position']
            organization = ScrapedOrganization()
            organization['name'] = contact_dicts[name]['organization']
            contact['organization'] = organization
            contacts.append(contact)
        return contacts


class OrganizationScraper():
    """A class that scrapes an Organization from a given page."""
    def __init__(self):
        self._scrapers = {
            'name': [OrgNameScraper],
            'address': [OrgAddressScraper],
            'types': [OrgTypeScraper],
            'phone_numbers': [USPhoneNumberScraper, IndianPhoneNumberScraper],
            'emails': [EmailScraper],
            'contacts': [ContactScraper],
            'organization_url': [OrgUrlScraper],
            'partners': [OrgPartnersScraper],
            'facebook': [OrgFacebookScraper],
            'twitter': [OrgTwitterScraper],
            'keywords': [KeywordScraper],
            'page_rank_info': [PageRankScraper]
        }
        self._multiple = ['types', 'phone_numbers', 'emails', 'partners', 'contacts']
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
                elif field == 'contacts':
                    organization[field] = []
                else:
                    # Get single field (e.g. name)
                    results = (self._scrapers[field][0])().parse(response)
                    if results:
                        organization[field] = results[0] if isinstance(results, type([])) else results
                    else:
                        organization[field] = None
        return organization

    def check_valid_org(self, response):
        """
        Checks if the current page is a valid page for an organization's homepage.

        Arguments:
            reponse (Response): Scrapy Response object of the page that is to be scraped.

        Returns:
            True if it's a valid organization page or already in the database.
            False if it's not the homepage.
        """
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
    """A class that scrapes Publications from Google Scholar."""
    def __init__(self):
        #Scrapers
        self.key_scraper = PublicationCitationSourceScraper()
        self.title_scraper = PublicationTitleScraper()
        self.author_scraper = PublicationAuthorsScraper()
        self.date_scraper = PublicationDateScraper()
        self.publisher_scraper = PublicationPublisherScraper()
        self.pub_url_scraper = PublicationURLScraper()
        self.titles = []
        self.publications = []

    #Second
    def parse_citation_page(self, response):
        """
        Gets the fields from the citation page and adds them to the Publication.

        Arguments:
            response (Response): Scrapy Response object of the page that is to be scraped.
        """
        pub = ScrapedPublication()
        pub['title'] = self.title_scraper.parse(response)
        self.titles.append(pub['title'])
        pub['authors'] = self.author_scraper.parse(response)
        pub['publication_date'] = self.date_scraper.parse(response)
        pub['publisher'] = self.publisher_scraper.parse(response)
        self.publications.append(pub)

    #Third
    def parse_pub_urls(self, response):
        """
        Gets all the publication urls.

        Arguments:
            response (Response): Scrapy Response object of the page that is to be scraped.
        """
        #Rescrape main page for links
        self.pub_url_scraper.seed_titles(self.titles)

        #Use original response now that we have the list of titles
        pub_urls = self.pub_url_scraper.parse(response)

        #Assign urls after scraping
        for index, publication in enumerate(self.publications):
            self.publications[index]['content_url'] = pub_urls[index]

    #First
    def parse_main_page(self, response):
        """Scrapes Google Scholar page for additional urls to crawl.

        Arguments:
            response (Response): Scrapy Response object for the page that is to be scraped.

        Returns:
            next_urls (list): List of citation URLs for the PublicationSpider to crawl.
        """
        #Must scrape several pubs at a time
        #Each page will have roughly 10 publications
        #Response is the main GS results page
        keys = self.key_scraper.parse(response)

        next_urls = []
        for key in keys:
            #All ajax calls use this format
            next_urls.append('scholar.google.com/scholar?q=info:' + key + ':scholar.google.com/&output=cite&scirp=0&hl=en')

        return next_urls
