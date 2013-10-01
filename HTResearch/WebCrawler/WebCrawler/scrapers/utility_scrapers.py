from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
from WebCrawler.items import *
import pdb
import re

# ALL OF THE TEMPLATE CONSTRUCTORS ARE JUST THERE SO THERE ARE NO ERRORS WHEN TESTING THE SCRAPERS THAT ARE DONE.
# Will likely remove/change them.

class ContactPositionScraper:

    def __init__(self):
        position = ""

class ContactPublicationsScraper:

    def __init__(self):
        publications = []

class EmailScraper:

    def __init__(self):
        emails = []

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        
        # body will get emails that are just text in the body
        body = hxs.select('//body').re(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}\b')
        
        # hrefs will get emails from hrefs
        hrefs = hxs.select("//./a[contains(@href,'@')]/@href").re(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}\b')
        
        emails = body+hrefs

        # Take out the unicode or whatever
        for i in range(len(emails)):
            emails[i] = emails[i].encode('ascii','ignore')

        # Makes it a set then back to a list to take out duplicates that may have been both in the body and links
        emails = list(set(emails))

        # Make the list an item
        email_list = []
        for email in emails:
            item = ScrapedEmail()
            item['email'] = email
            email_list.append(item)

        return email_list

class NameScraper:

    def __init__(self):
        names = []

class OrgAddressScraper:

    def __init__(self):
        addresses = []

class OrgContactsScraper:

    def __init__(self):
        contacts = []

class OrgPartnersScraper:

    def __init__(self):
        partners = []

class OrgTypeScraper:

    def __init__(self):
        types = []

class PhoneNumberScraper:

    def __init__(self):
        phone_numbers = []

class PublicationAuthorsScraper:

    def __init__(self):
        authors = []

class PublicationDateScraper:

    def __init__(self):
        partners = []

class PublicationPublisherScraper:

    def __init__(self):
        publisher = []

class PublicationTitleScraper:

    def __init__(self):
        titles = []

class PublicationTypeScraper:

    def __init__(self):
        type = []
