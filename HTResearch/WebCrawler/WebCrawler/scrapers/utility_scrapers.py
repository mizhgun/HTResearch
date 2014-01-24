import itertools
import os
import re
from urlparse import urlparse, urljoin
import string
import datetime
import hashlib
import operator
from sgmllib import SGMLParseError

from nltk import FreqDist, WordNetLemmatizer
from scrapy.selector import HtmlXPathSelector
from scrapy.selector import XPathSelectorList
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from bson.binary import Binary

from ..items import *
from HTResearch.DataAccess.dao import *
from HTResearch.Utilities.converter import *
from HTResearch.Utilities.logutil import *
from link_scraper import LinkScraper
from HTResearch.DataModel.enums import OrgTypesEnum



# ALL OF THE TEMPLATE CONSTRUCTORS ARE JUST THERE SO THERE ARE NO ERRORS WHEN TESTING THE SCRAPERS THAT ARE DONE.
# Will likely remove/change them.

_utilityscrapers_logger = get_logger(LoggingSection.CRAWLER, __name__)


class ContactNameScraper(object):
    def __init__(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../Resources/names.txt'), 'r') as f:
            names = f.read().splitlines()
            self._names = [name.title() for name in names]
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../Resources/lastnames.txt'), 'r') as f:
            lnames = f.read().splitlines()
            self._last_names = [lname.title() for lname in lnames]

        self._titles = ['Mr', 'Mrs', 'Ms', 'Miss', 'Dr', 'Sh', 'Smt', 'Prof', 'Shri']
        length = len(self._titles)
        # catch Dr and Dr.
        for i in range(0, length):
            self._titles.append(self._titles[i]+'.')

        # Make a regex check for if a potential name is actually a date. Not concerned with months that aren't in the
        # names list
        self._date = re.compile(r'Jan ([0-9]{4}|[0-9]{1,2}|[0-9]{1,2}(rd|th|nd)?)|'
                                r'April ([0-9]{4}|[0-9]{1,2}|[0-9]{1,2}(rd|th|nd)?)|'
                                r'May ([0-9]{4}|[0-9]{1,2}|[0-9]{1,2}(rd|th|nd)?)|'
                                r'June ([0-9]{4}|[0-9]{1,2}|[0-9]{1,2}(rd|th|nd)?)|'
                                r'August ([0-9]{4}|[0-9]{1,2}|[0-9]{1,2}(rd|th|nd)?)')

        #Load words to be ignored
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../Resources/stopwords.txt')) as f:
            self._stopwords = f.read().splitlines()
            self._stopwords = [word.title() for word in self._stopwords]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        body = hxs.select('//body//text()').extract()
        body = [s.strip() for s in body if s.strip()]
        names = []

        for s in body:
            str_split = s.split()
            i = len(str_split) - 1
            name_to_add = ""
            # start at the back of string to get last name and then get all previous names
            while i >= 0:
                split_index = str_split[i]

                # variables for below elif to not be so terrifying
                stop_word = split_index not in self._stopwords or len(split_index) == 1
                uppercase = split_index.istitle() or split_index.isupper()
                all_alpha = all(c.isalpha() or c == '.' for c in split_index)

                # if it's in the last names and it isn't the first word in the string
                if split_index in self._last_names and split_index != str_split[0]:
                    name_to_add = split_index + " " + name_to_add

                # if in first names
                elif split_index in self._names:
                    name_to_add = split_index + " " + name_to_add

                    # if the last name wasn't caught but first name was and next word is last name format
                    try:
                        next_uppercase = str_split[i+1].istitle() or str_split[i+1].isupper()
                        next_all_alpha = all(c.isalpha() or c == '.' for c in str_split[i+1])
                        if next_uppercase and str_split[i+1] not in self._stopwords and \
                                next_all_alpha and str_split[i+1] not in name_to_add:
                            name_to_add += str_split[i+1]
                    except IndexError:
                        pass

                # will catch a first name if a last name has been caught and if it's in correct name format
                elif stop_word and split_index not in self._titles and uppercase and all_alpha and name_to_add:
                    name_to_add = split_index + " " + name_to_add
                elif not split_index.istitle():
                    break
                i -= 1

            # only get names that are both first and last name
            if name_to_add and len(name_to_add.split()) > 1:
                names.append(name_to_add)
        names = [name.encode('ascii', 'ignore') for name in names]
        items = []
        for i in range(len(names)):
            item = ScrapedContactName()
            item['name'] = names[i].strip()
            items.append(item)
        return items


class ContactPositionScraper(object):
    def __init__(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../Resources/positions.txt')) as f:
            self._positions = f.read().splitlines()
        self._tag = re.compile(r'<[A-Za-z0-9]*>|<[A-Za-z0-9]+|</[A-Za-z0-9]*>')
        self._remove_attributes = re.compile(r'<([A-Za-z][A-Za-z0-9]*)[^>]*>')

    def parse(self, response):
        for position in self._positions:
            if string.find(response.body, position) is not -1:
                return position


class ContactPublicationsScraper(object):
    def __init__(self):
        self.publications = []


class EmailScraper(object):
    def __init__(self):
        self.email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+\[at][A-Za-z0-9.-]+\[dot][A-Za-z]{2,4}\b|'
                                      r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}\b|'
                                      r'\b[A-Za-z0-9._%+-]+ at [A-Za-z0-9.-]+ dot [A-Za-z]{2,4}\b|'
                                      r'\b[A-Za-z0-9._%+-]+\(at\)[A-Za-z0-9.-]+\(dot\)[A-Za-z]{2,4}\b')
        self.c_data = re.compile(r'(.*?)<!\[CDATA(.*?)]]>(.*?)', re.DOTALL)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        # body will get emails that are just text in the body
        body = hxs.select('//body//text()')

        # Remove C_Data tags, since they are showing up in the body text for some reason
        body = XPathSelectorList([text for text in body if not (re.match(self.c_data, text.extract()) or
                                                                text.extract().strip() == '')])

        body = body.re(self.email_regex)

        # hrefs will get emails from hrefs
        hrefs = hxs.select("//./a[contains(@href,'@')]/@href").re(self.email_regex)

        emails = body + hrefs

        # Take out the unicode or whatever, and substitute [at] for @ and [dot] for .
        for i in range(len(emails)):
            emails[i] = emails[i].encode('ascii', 'ignore')
            emails[i] = re.sub(r'(\[at]|\(at\)| at )([A-Za-z0-9.-]+)(\[dot]|\(dot\)| dot )', r'@\2.', emails[i])

        # Makes it a set then back to a list to take out duplicates that may have been both in the body and links
        emails = list(set(emails))

        return emails


class KeywordScraper(object):
    NUM_KEYWORDS = 50
    _stopwords = []
    _lemmatizer = WordNetLemmatizer()

    def __init__(self):
        #Load words to be ignored
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../Resources/stopwords.txt')) as f:
            self._stopwords = f.read().splitlines()

    def format_extracted_text(self, list):
        for i in range(len(list)):
            list[i] = list[i].encode('ascii', 'ignore')
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
                        append_to.append(self._lemmatizer.lemmatize(word))

        return append_to

    def parse(self, response):
        all_words = []

        #Parse the response
        hxs = HtmlXPathSelector(response)

        elements = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'a', 'b', 'code', 'em', 'italic',
                    'small', 'strong', 'div', 'span', 'li', 'th', 'td', 'a[contains(@href, "image")]']

        for element in elements:
            words = hxs.select('//' + element + '/text()').extract()
            all_words = self.append_words(all_words, words)

        #Run a frequency distribution on the web page body
        all_words_no_punct = [word.translate(None, string.punctuation) for word in all_words]
        freq_dist = FreqDist(all_words_no_punct)

        #Remove ignored words
        for word in self._stopwords:
            if word in freq_dist:
                del freq_dist[word]

        # Take the NUM_KEYWORDS most frequent keywords
        most_freq_keywords = dict(
            sorted(freq_dist.iteritems(), key=operator.itemgetter(1), reverse=True)[:self.NUM_KEYWORDS])
        return most_freq_keywords


class IndianPhoneNumberScraper(object):
    def __init__(self):
        self._india_format_regex = re.compile(r'\b(?!\s)(?:91[-./\s]+)?[0-9]+[0-9]+[-./\s]?[0-9]?[0-9]?[-./\s]?[0-9]?'
                                              r'[-./\s]?[0-9]{5}[0-9]?\b|\b(?!\s)(?:91[-./\s]+)?[0-9]+[0-9]+[-./\s]?'
                                              r'[0-9]?[0-9]?[-./\s]?[0-9]{4}[-./\s]?[0-9]{4}\b')

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        # body will get phone numbers that are just text in the body
        body = hxs.select('//body').re(self._india_format_regex)

        phone_nums = body

        # Remove unicode indicators
        for i in range(len(phone_nums)):
            phone_nums[i] = phone_nums[i].encode('ascii', 'ignore')

        # Makes it a set then back to a list to take out duplicates that may have been both in the body and links
        phone_nums = list(set(phone_nums))

        # Make the list an item
        phone_nums_list = []
        for num in phone_nums:
            num = re.sub("\D", "", num)
            # removing ScrapedPhoneNumber() item in favor of returning exactly what DB expects
            # Paul Poulsen
            #number = ScrapedPhoneNumber()
            #number["phone_number"] = num
            phone_nums_list.append(num)

        return phone_nums_list


class OrgAddressScraper(object):
    def __init__(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../Resources/cities.txt')) as f:
            self._cities = f.read().splitlines()

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        body = hxs.select('//body//text()').extract()
        for i in range(len(body)):
            body[i] = (body[i].encode('ascii', 'ignore')).strip()
            body[i] = "".join((char if char.isalnum() else " ") for char in body[i]).split()
        body = list(flatten(body))

        # This loop will check if city is in the body, if it is, find all occurrences of that city in the body,
        # and then it will check all the occurring indices, and if the next index (or next 2 indices) is the zip code
        city_and_zip = []
        for city in self._cities:
            city = city.strip()
            if city in body:
                indices = [i for i, x in enumerate(body) if x == city]
                for i in indices:
                    # because the body is separated by spaces, "New Delhi" would be in separate indices, so
                    # check if the index before it could add to the city name and still be valid
                    # EX: "Delhi" is valid and "New Delhi" is valid
                    check = body[i]
                    counter = 0
                    while check in self._cities:
                        city = check
                        check = body[i - 1 - counter] + " " + city
                        counter += 1
                    if len(body[i + 1]) == 6 and body[i + 1].isdigit():
                        city_and_zip.append((city, body[i + 1]))
                    elif len(body[i + 1]) == 3 and len(body[i + 2]) == 3 and body[i + 1].isdigit() and body[
                                i + 2].isdigit():
                        city_and_zip.append((city, body[i + 1] + body[i + 2]))
        address_list = []
        for i in range(len(city_and_zip)):
            item = ScrapedAddress()
            item['city'] = city_and_zip[i][0]
            item['zip_code'] = city_and_zip[i][1]
            address_list.append(item)
            # the database is expecting a single string, so I'm going to just return first for now -Paul-
        return address_list[0]['city'] + " " + address_list[0]['zip_code'] if len(address_list) > 0 else ''


class OrgContactsScraper(object):
    def __init__(self):
        self._name_scraper = ContactNameScraper()
        self._number_scraper = IndianPhoneNumberScraper()
        self._email_scraper = EmailScraper()
        self._position_scraper = ContactPositionScraper()
        self._org_name_scraper = OrgNameScraper()
        self._contacts = []

    def parse(self, response):
        contact_indices = []

        names = self._name_scraper.parse(response)
        org_name = self._org_name_scraper.parse(response)
        if names is not None:
            self._contacts = {name.get('name'): {} for name in names}
            for name in names:
                n = string.find(response.body, name.get('name'))    #find the index of each contact so we can search
                contact_indices.append(n)                           #only between the contacts for their info
        for i in range(len(names)):
            if i < len(names) - 1:
                cr = response.replace(body=response.body[contact_indices[i]:contact_indices[i + 1]])
            else:
                cr = response.replace(body=response.body[contact_indices[i]:])
            self._contacts[names[i].get('name')]['position'] = [self._position_scraper.parse(cr)
                                                          if self._position_scraper.parse(cr)
                                                          else None][0]
            self._contacts[names[i].get('name')]['number'] = [self._number_scraper.parse(cr)[0]
                                                        if self._number_scraper.parse(cr)
                                                        else None][0]
            self._contacts[names[i].get('name')]['email'] = [self.compare_emails(cr, names[i].get('name'))
                                                       if self.compare_emails(cr, names[i].get('name'))
                                                       else None][0]
            self._contacts[names[i].get('name')]['organization'] = org_name
        return self._contacts

    def compare_emails(self, response, name):
        emails = self._email_scraper.parse(response)
        name_split = name.split()
        for email in emails:
            for split_index in name_split:
                if split_index.lower() in email:
                    return email
        return emails[0]


class OrgFacebookScraper(object):
    def __init__(self):
        regex_allow = re.compile("^(?:(?:http|https)://)?(?:www\.)?facebook\.com/.+(?:/)?$", re.IGNORECASE)
        self.fb_link_ext = SgmlLinkExtractor(allow=regex_allow, canonicalize=False, unique=True)

    def parse(self, response):
        try:
            fb_links = self.fb_link_ext.extract_links(response)
        except SGMLParseError as e:
            # Page was poorly formatted, oh well
            _utilityscrapers_logger.error('Exception encountered when link extracting page: %s' % str(response.url))
            return None

        urls = [x.url for x in fb_links]
        if len(fb_links) > 0:
            return urls[0]
        return None


class OrgTwitterScraper(object):
    def __init__(self):
        regex_allow = re.compile("^(?:(?:http|https)://)?(?:www\.)?twitter\.com/(?:#!/)?\w+(?:/)?$", re.IGNORECASE)
        self.tw_link_ext = SgmlLinkExtractor(allow=regex_allow, canonicalize=False, unique=True)

    def parse(self, response):
        try:
            tw_links = self.tw_link_ext.extract_links(response)
        except SGMLParseError as e:
            # Page was poorly formatted, oh well
            _utilityscrapers_logger.error('Exception encountered when link extracting page: %s' % str(response.url))
            return None

        urls = [x.url for x in tw_links]
        if len(urls) > 0:
            return urls[0]
        return None


class OrgNameScraper(object):
    def __init__(self):
        self._split_punctuation = re.compile(r"[ \w']+")
        #Load words to be ignored
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../Resources/stopwords.txt')) as f:
            self._stopwords = f.read().splitlines()

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        url = response.url
        url = urlparse(url).netloc
        url = url.split('.')

        # url contains a www. or something like that
        if len(url) > 2:
            url = url[1]
        # otherwise there's no www.
        else:
            url = url[0]

        title_tag = hxs.select('//./title/text()').extract()[0]
        title_tag = re.findall(self._split_punctuation, title_tag)

        org_name = ScrapedOrgName()
        org_name['name'] = ''
        for potential_name in title_tag:
            # first check if whole string is the url
            whole_string = potential_name.replace(' ', '').lower()
            if whole_string == url:
                org_name['name'] = potential_name.encode('ascii', 'ignore').strip()
                break

            # check if parts of the string is the url
            potential_name_split = potential_name.split()
            for i, split_element in enumerate(potential_name_split):
                split_element = split_element.lower()
                if split_element in url:
                    org_name['name'] = potential_name.encode('ascii', 'ignore').strip()
                    break

            # check if the initials are the url (not just in it)
            acronym = "".join(item[0].lower() for item in potential_name_split if item not in self._stopwords)
            if acronym == url:
                org_name['name'] = potential_name.encode('ascii', 'ignore').strip()
                break
                # Returning string instead of ScrapedOrgName to make transition to DB easier
        return org_name['name']


class OrgPartnersScraper(object):
    def __init__(self):
        self._link_scraper = LinkScraper()
        self._partner_text = 'partner'
        self._netloc_ignore = [
            'youtube.com',
            'www.youtube.com',
            'google.com',
            'www.google.com',
            'twitter.com',
            'www.twitter.com',
            'facebook.com',
            'www.facebook.com',
            'bit.ly',
            'ow.ly',
        ]

    # Find the path to selected node(s)
    def _path_to(self, sel):
        path = ''
        while sel:
            tags = sel.select('name()').extract()
            path = '/%s%s' % (tags[0], path)
            sel = sel.select('..')
        return path

    # Find out how many external links are in a list
    # (returns 0 if not all external links)
    def _external_link_count(self, page_url, sel):
        count = 0
        checked_netlocs = []
        for href in sel.select('@href').extract():
            link_url = urlparse(urljoin(page_url.geturl(), href))
            # link is external
            if link_url.netloc != page_url.netloc:
                # link is not to an ignored netloc
                if link_url.netloc not in self._netloc_ignore:
                    checked_netlocs.append(link_url.netloc)
                    count += 1
        return count

    def parse(self, response):

        hxs = HtmlXPathSelector(response)
        partners = []

        # Look for a tag indicating partnerships (not inside links)
        elements = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', ]
        partner_page = False
        for e in elements:
            found = hxs.select(
                "//%s[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'partner')]" % e)
            if found and '/a/' not in self._path_to(found):
                partner_page = True
                break

        # Only scrape partner organizations if this page indicates that it lists partners
        if partner_page:
            page_url = urlparse(response.url)

            # Find the largest group of external links on the page
            partner_links = []
            checked_paths = []
            max_count = 0
            all_links = hxs.select('//a')
            for link in all_links:
                path = self._path_to(link)
                # Don't check groups of links more than once
                if path not in checked_paths:
                    checked_paths.append(path)
                    related_links = hxs.select(path)
                    count = self._external_link_count(page_url, related_links)
                    if count > max_count:
                        max_count = count
                        partner_links = related_links

            # Add organizations with links' URLs
            partner_hrefs = partner_links.select('@href').extract()
            for href in partner_hrefs:
                link_url = urlparse(urljoin(page_url.geturl(), href))
                if link_url.netloc not in self._netloc_ignore + [page_url.netloc]:
                    partner = ScrapedOrganization()
                    partner['organization_url'] = '%s/' % link_url.netloc
                    partners.append(partner)

        return partners


class OrgTypeScraper(object):
    def __init__(self):
        # Lemmatizer for shortening each word to a more-commonly-used form of the word
        self._lemmatizer = WordNetLemmatizer()
        # Scraper to get common keywords from response
        self._keyword_scraper = KeywordScraper
        # Maximum number of types
        self._max_types = 3
        # Obvious religious keywords. These must be lowercase
        self._religion_words = ['god', 'spiritual', 'religion', 'worship', 'church', 'prayer']
        # Regex for url of government websites
        self._government_detector = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[Gg][Oo][Vv](\.[a-zA-Z]{2})?$'
        # Lowest (highest number) rank a keyword can have and still count towards determining organization type
        self._max_rank = 40
        # Keywords to look for for other types. These must be lowercase
        self._type_words = {
            OrgTypesEnum.EDUCATION: [
                'education',
                'school',
                'study',
                'teach',
            ],
            OrgTypesEnum.ADVOCACY: [
                'advocacy',
                'lobby',
                'policy',
            ],
            OrgTypesEnum.RESEARCH: [
                'research',
                'conduct',
                'document',
                'identify',
                'analyze',
                'correlate',
                'compile',
                'report',
                'data',
                'publication',
                'journal',
                'periodical',
                'newsletter',
            ],
            OrgTypesEnum.PREVENTION: [
                'prevention',
                'intervention',
                'education',
                'development',
                'community',
                'ownership',
            ],
            OrgTypesEnum.PROTECTION: [
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
                'women',
            ],
            OrgTypesEnum.PROSECUTION: [
                'prosecution',
                'compliance',
                'abolish',
                'law',
                'enforcement',
                'regulatory',
                'regulation',
                'justice',
            ],
        }

        # Stem search words (religious, general)
        self._religion_words = [self._lemmatizer.lemmatize(word) for word in self._religion_words]
        for key in self._type_words.iterkeys():
            self._type_words[key] = [self._lemmatizer.lemmatize(word) for word in self._type_words[key]]

    # Find the minimum index of a term from a search list in a list
    @staticmethod
    def _min_index_found(listwords, searchwords):
        index = float('inf')
        for word in searchwords:
            if word in listwords:
                index = min(index, listwords.index(word))
        return index

    # Get the organization type
    def parse(self, response):
        keyword_scraper_inst = self._keyword_scraper()

        # Get keywords
        keywords_dict = keyword_scraper_inst.parse(response)
        keywords = map(lambda (k, v): k, sorted(keywords_dict.items(), key=lambda (k, v): v, reverse=True))

        # Get all words
        all_words = []
        hxs = HtmlXPathSelector(response)
        elements = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'a', 'b', 'code', 'em', 'italic',
                    'small', 'strong', 'div', 'span', 'li', 'th', 'td', 'a[contains(@href, "image")]']
        for element in elements:
            words = hxs.select('//' + element + '/text()').extract()
            keyword_scraper_inst.append_words(all_words, words)

        all_words = list(set(self._lemmatizer.lemmatize(word) for word in all_words))

        types = []
        # Government: check the URL
        if re.search(self._government_detector, urlparse(response.url).netloc):
            types.append(OrgTypesEnum.GOVERNMENT)
        # Religion: check for the appearance of certain religious terms
        # (this means that government and religion types are mutually exclusive)
        elif any(word in self._religion_words for word in all_words):
            types.append(OrgTypesEnum.RELIGIOUS)
            # Other types
        for type in self._type_words.iterkeys():
            rank = self._min_index_found(keywords, self._type_words[type])
            if rank < self._max_rank:
                types.append(type)
            if len(types) >= self._max_types:
                break

        return types or [OrgTypesEnum.UNKNOWN]


class OrgUrlScraper(object):
    def __init__(self):
        pass

    def parse(self, response):
        parse = urlparse(response.url)
        url = '%s/' % (parse.netloc)
        return url


class PublicationAuthorsScraper(object):
    def __init__(self):
        authors = []


class PublicationDateScraper(object):
    def __init__(self):
        partners = []


class PublicationPublisherScraper(object):
    def __init__(self):
        publisher = []


class PublicationTitleScraper(object):
    def __init__(self):
        titles = []


class PublicationTypeScraper(object):
    def __init__(self):
        type = []


class UrlMetadataScraper(object):
    def __init__(self):
        self.dao = URLMetadataDAO

    def parse(self, response):
        # Initialize item and set url
        metadata = ScrapedUrl()
        metadata['url'] = response.url
        metadata['last_visited'] = datetime.utcnow()

        # calculate new hash
        md5 = hashlib.md5()
        md5.update(response.body)
        # python hashlib doesn't output integers, so we have to do it ourselves.
        hex_hash = md5.hexdigest()
        # this will be a 128 bit number
        # Don't use the subtype argument, as it doesn't get stored to mongo and makes comparisons harder
        metadata['checksum'] = Binary(data=bytes(int(hex_hash, 16)))

        # default values for first time
        metadata['update_freq'] = 0

        # Compare checksums and update update_freq using the existing URL
        exist_url_dto = self.dao().find(url=response.url)
        if exist_url_dto is not None:
            exist_url = DTOConverter.from_dto(URLMetadataDTO, exist_url_dto)
            if exist_url.checksum is not None:
                if exist_url.update_freq is not None:
                    if exist_url.checksum != metadata['checksum']:
                        # Checksums differ and update_freq has been initialized, so increment
                        metadata['update_freq'] = exist_url.update_freq + 1
                    else:
                        # Checksums are the same and update_freq was initialized, so set
                        metadata['update_freq'] = exist_url.update_freq
                else:
                    if exist_url.checksum != metadata['checksum']:
                        # Checksums differ but update_freq was not initialized to zero, so set to 1
                        metadata['update_freq'] = 1
                    else:
                        # Checksums are the same but update_freq wasn't initialized, so initialize to 0
                        metadata['update_freq'] = 0

        # if the existing checksum was None, set the checksum and update_freq to 0 (above),
        # as this should be the first time we've seen this page

        # TODO: Score the page.
        # Ideas for page scoring:  Simple Google PageRank using references to/from other pages; Keyword Search;
        # Update frequency; User Feedback (the more a page is clicked the more we want to keep it updated)

        return metadata


class USPhoneNumberScraper(object):
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        us_format_regex = re.compile(
            r'\b(?! )1?\s?[(-./]?\s?[2-9][0-8][0-9]\s?[)-./]?\s?[2-9][0-9]{2}\s?\W?\s?[0-9]{4}\b')
        # body will get phone numbers that are just text in the body
        body = hxs.select('//body').re(us_format_regex)

        phone_nums = body

        # Remove unicode indicators
        for i in range(len(phone_nums)):
            phone_nums[i] = phone_nums[i].encode('ascii', 'ignore')

        # Makes it a set then back to a list to take out duplicates that may have been both in the body and links
        phone_nums = list(set(phone_nums))

        # Make the list an item
        phone_nums_list = []
        for num in phone_nums:
            num = re.sub("\D", "", num)
            # Removing item in favor of giving data ready for DB
            # Paul Poulsen
            #number = ScrapedPhoneNumber()
            #number["phone_number"] = num
            phone_nums_list.append(num)

        return phone_nums_list


def flatten(l):
    # Flatten one level of nesting
    return itertools.chain.from_iterable(l)
