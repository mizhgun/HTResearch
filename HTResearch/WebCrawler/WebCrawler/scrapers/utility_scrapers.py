from scrapy.selector import HtmlXPathSelector
from ..items import *
import itertools
import re
import urlparse
import string

# ALL OF THE TEMPLATE CONSTRUCTORS ARE JUST THERE SO THERE ARE NO ERRORS WHEN TESTING THE SCRAPERS THAT ARE DONE.
# Will likely remove/change them.


class ContactPositionScraper:

    def __init__(self):
        self.position = ""


class ContactPublicationsScraper:

    def __init__(self):
        self.publications = []


class EmailScraper:
    def parse(self, response):
        email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+\[at][A-Za-z0-9.-]+\[dot][A-Za-z]{2,4}\b|'
                                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}\b|'
                                r'\b[A-Za-z0-9._%+-]+ at [A-Za-z0-9.-]+ dot [A-Za-z]{2,4}\b|'
                                r'\b[A-Za-z0-9._%+-]+\(at\)[A-Za-z0-9.-]+\(dot\)[A-Za-z]{2,4}\b')
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

class KeywordScraper:
    NUM_KEYWORDS = 50
    stopwords = []
    def __init__(self):
        self.savedPath = os.getcwd()
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        #Load words to be ignored
        with open("../Resources/stopwords.txt") as f:
            self.stopwords = f.read().splitlines()

    def __del__( self ):
        os.chdir( self.savedPath )

    def format_extracted_text(self, list):

        for i in range(len(list)):
            list[i] = list[i].encode('ascii','ignore')
        return list
            
    def append_words(self, append_to, source):
        if not source:
            return append_to

        #Split each array into sentence, and those into words
        for line in self.format_extracted_text(source):
            line = string.lower(line)
            for c in string.punctuation:
                line = line.replace(c, "")
                for word in line.split():
                    if not word.isdigit():
                        append_to.append(word)

        return append_to
            
    def parse(self, response):
        all_words = []

        #Parse the response
        hxs = HtmlXPathSelector(response)

        elements = ['h1', 'h2','h3','h4','h5','h6','p','a','b','code','em','italic',
                    'small','strong','div','span','li','th','td','a[contains(@href, "image")]']

        for element in elements:
            words = hxs.select('//'+element+'/text()').extract()
            all_words = self.append_words(all_words, words)

        #Run a frequency distribution on the web page body
        freq_dist = FreqDist(all_words)

        #Parse the distribution into individual words without frequencies
        keywords = freq_dist.keys()

        #Remove ignored words
        parsed_keywords = [word for word in keywords if word not in self.stopwords]

        most_freq_keywords = parsed_keywords[:self.NUM_KEYWORDS]
        return most_freq_keywords

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
        self.names = []


class OrgAddressScraper:
    def __init__(self):
        with open("../Resources/cities.txt") as f:
            self.cities = f.read().splitlines()

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        body = hxs.select('//body//text()').extract()
        for i in range(len(body)):
            body[i] = (body[i].encode('ascii', 'ignore')).strip()
            body[i] = "".join((char if char.isalnum() else " ") for char in body[i]).split()
        body = list(self.flatten(body))

        # This loop will check if city is in the body, if it is, find all occurrences of that city in the body,
        # and then it will check all the occurring indices, and if the next index (or next 2 indices) is the zip code
        city_and_zip = []
        for city in self.cities:
            city = city.strip()
            if city in body:
                indices = [i for i, x in enumerate(body) if x == city]
                for i in indices:
                    # because the body is separated by spaces, "New Delhi" would be in separate indices, so
                    # check if the index before it could add to the city name and still be valid
                    # EX: "Delhi" is valid and "New Delhi" is valid
                    check = body[i]
                    counter = 0
                    while check in self.cities:
                        if check in self.cities:
                            city = check
                        check = body[i-1-counter] + " " + city
                        counter += 1
                    if len(body[i+1]) == 6 and body[i+1].isdigit():
                        city_and_zip.append((city, body[i+1]))
                    elif len(body[i+1]) == 3 and len(body[i+2]) == 3 and body[i+1].isdigit() and body[i+2].isdigit():
                        city_and_zip.append((city, body[i+1] + body[i+2]))
        address_list = []
        for i in range(len(city_and_zip)):
            item = ScrapedAddress()
            item['city'] = city_and_zip[i][0]
            item['zip_code'] = city_and_zip[i][1]
            address_list.append(item)
        return address_list

    @staticmethod
    def flatten(l):
        # Flatten one level of nesting
        return itertools.chain.from_iterable(l)


class OrgContactsScraper:

    def __init__(self):
        self.contacts = []


class OrgPartnersScraper:

    def __init__(self):
        self.partners = []


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

<<<<<<< HEAD
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
=======
>>>>>>> R1_SeekingJustice

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
