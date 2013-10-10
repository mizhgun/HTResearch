from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
from nltk.stem.porter import PorterStemmer
from scrapy.http import TextResponse
import math
from ..items import *
import pdb
import re
import urlparse

# ALL OF THE TEMPLATE CONSTRUCTORS ARE JUST THERE SO THERE ARE NO ERRORS WHEN TESTING THE SCRAPERS THAT ARE DONE.
# Will likely remove/change them.

class ContactPositionScraper:

    def __init__(self):
        position = ""

class ContactPublicationsScraper:

    def __init__(self):
        publications = []

class EmailScraper:
    def parse(self, response):
        email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+\[at][A-Za-z0-9.-]+\[dot][A-Za-z]{2,4}\b|\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}\b|\b[A-Za-z0-9._%+-]+ at [A-Za-z0-9.-]+ dot [A-Za-z]{2,4}\b|\b[A-Za-z0-9._%+-]+\(at\)[A-Za-z0-9.-]+\(dot\)[A-Za-z]{2,4}\b')
        hxs = HtmlXPathSelector(response)

        # body will get emails that are just text in the body
        body = hxs.select('//body').re(email_regex)
        
        # hrefs will get emails from hrefs
        hrefs = hxs.select("//./a[contains(@href,'@')]/@href").re(email_regex)
        
        emails = body+hrefs

        # Take out the unicode or whatever, and substitute [at] for @ and [dot] for .
        for i in range(len(emails)):
            emails[i] = emails[i].encode('ascii','ignore')
            emails[i] = re.sub(r'(\[at]|\(at\)| at )([A-Za-z0-9.-]+)(\[dot]|\(dot\)| dot )', r'@\2.', emails[i])

        # Makes it a set then back to a list to take out duplicates that may have been both in the body and links
        emails = list(set(emails))

        # Make the list an item
        email_list = []
        for email in emails:
            item = ScrapedEmail()
            item['email'] = email
            email_list.append(item)

        return email_list

class IndianPhoneNumberScraper:
    
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        india_format_regex = re.compile(r'\b(?!\s)(?:91[-./\s]+)?[0-9]+[0-9]+[-./\s]?[0-9]?[0-9]?[-./\s]?[0-9]?[-./\s]?[0-9]{5}[0-9]?\b')
        # body will get phone numbers that are just text in the body
        body = hxs.select('//body').re(india_format_regex)

        phone_nums = body 

        # Remove unicode indicators
        for i in range(len(phone_nums)):
            phone_nums[i] = phone_nums[i].encode('ascii','ignore')

        # Makes it a set then back to a list to take out duplicates that may have been both in the body and links
        phone_nums = list(set(phone_nums))

        # Make the list an item
        phone_nums_list = []
        for num in phone_nums:
            item = ScrapedPhoneNumber()
            item['phone_number'] = num
            phone_nums_list.append(item)

        return phone_nums_list

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

        self._keyword_scraper = KeywordScraper()
        self._type_count = 3
        self._religion_terms = [ 'God', 'spiritual', 'religion', 'worship', 'church' ]
        self._government_detector = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[Gg][Oo][Vv](\.[a-zA-Z]{2})?$'
        # Lowest (highest number) rank a keyword can have and still count towards determining organization type
        self._max_rank = 5
        self._type_terms = {
            """'religious': [
                'religious',
                'God',
                'worship',
                'church',
                'spiritual',
            ],
            'government': [
                'government',
                'act',
                'nation',
                'state',
                'department',
                'united',
                'investigation',
                'intervention',
                'legislation',
                'agency',
                'court',
                'bill',
                'committee',
                'law',
                'enforcement',
                'legal',
                'conviction',
                'ministry',
                'secretary',
                'agency',
            ],"""
            'education': [
                'education',
                'school',
                'study',
                'teach',
            ],
            'advocacy': [
                'lobbying',
                'policy',
                'legal',
                'media',
                'change',
                'government',
                'state',
                'court',
            ],
            'research': [
                'research',
                'conduct',
                'documentation',
                'study',
                'identify',
                'analysis',
                'understand',
                'find',
                'insight',
                'link',
                'correlation',
                'compile',
                'report',
                'data',
                'publication',
                'book',
                'journal',
                'periodical',
                'newsletter',
            ],
            'prevention': [
                'prevention',
                'intervention',
                'education',
                'development',
                'community',
                'ownership',
            ],
            'protection': [
                'protection',
                'rescue',
                'rehabilitation',
                'reintegration',
                'repatriation',
                'empowerment',
                'repatriation',
                'fulfilment',
                'freedom',
                'opportunity',
            ],
            'prosecution': [
                'prosecution',
                'compliance',
                'abolish',
                'law',
                'enforcement',
                'regulatory',
            ],
        }

        # List of document term lists
        self._documents = []

    # Find the minimum
    def _min_index_found(self, listWords, searchWords):
        return listWords.index(min(searchWords, key=lambda word: listWords.index(word) if word in listWords else float('inf')))
    
    # Get the organization type
    def parse(self, response):
            
        # Get keywords
        keywords = self._keyword_scraper.parse(response)

        types = []

        # Government: check the URL
        if re.search(self._government_detector, urlparse(response.url).netloc):
            types.append('government')
        # Religion: check for the appearance of certain religious terms
        # Note that government and religion are mutually exclusive
        elif any(term in self._religion_terms for term in keywords):
            types.append('religion')
        # Other types
        #sorted(self._type_terms.iterkeys(), key=lambda searchwords: self._min_index_found(keywords, searchwords)
        indices = {}
        for type in self._type_terms.iterkeys():
            rank = self._min_index_found(keywords, self._type_terms[type])
            if rank < self._max_rank:
                types.append(type)

        return types

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

class USPhoneNumberScraper:
           
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        us_format_regex = re.compile(r'\b(?! )1?\s?[(-./]?\s?[2-9][0-8][0-9]\s?[)-./]?\s?[2-9][0-9]{2}\s?\W?\s?[0-9]{4}\b')
        # body will get phone numbers that are just text in the body
        body = hxs.select('//body').re(us_format_regex)

        phone_nums = body 

        # Remove unicode indicators
        for i in range(len(phone_nums)):
            phone_nums[i] = phone_nums[i].encode('ascii','ignore')

        # Makes it a set then back to a list to take out duplicates that may have been both in the body and links
        phone_nums = list(set(phone_nums))

        # Make the list an item
        phone_nums_list = []
        for num in phone_nums:
            item = ScrapedPhoneNumber()
            item['phone_number'] = num
            phone_nums_list.append(item)

        return phone_nums_list
