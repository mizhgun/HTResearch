import itertools
import os
import re
from urlparse import urlparse, urljoin
import string
import datetime
import hashlib
import operator

from nltk import FreqDist, WordNetLemmatizer
from scrapy.selector import HtmlXPathSelector
from scrapy.selector import XPathSelectorList
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from bson.binary import Binary
from springpython.context import ApplicationContext

from HTResearch.WebCrawler.WebCrawler.items import *
from HTResearch.DataAccess.dao import *
from HTResearch.Utilities.converter import *
from HTResearch.Utilities.context import DAOContext
from HTResearch.WebCrawler.WebCrawler.scrapers.link_scraper import LinkScraper
from HTResearch.DataModel.enums import OrgTypesEnum
from dao import MockURLMetadataDAO


# ALL OF THE TEMPLATE CONSTRUCTORS ARE JUST THERE SO THERE ARE NO ERRORS WHEN TESTING THE SCRAPERS THAT ARE DONE.
# Will likely remove/change them.


class MockContactNameScraper:
    # TODO: Find list of Indian names and add them to names.txt
    def __init__(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               '../../WebCrawler/WebCrawler/Resources/names.txt')) as f:
        #with open('../../../WebCrawler/WebCrawler/Resources/names.txt') as f:
            self._names = f.read().splitlines()
        self._titles = ['Mr', 'Mrs', 'Ms', 'Miss', 'Dr']
        self._tag = re.compile(r'<[A-Za-z0-9]*>|<[A-Za-z0-9]+|</[A-Za-z0-9]*>')
        self._remove_attributes = re.compile(r'<([A-Za-z][A-Za-z0-9]*)[^>]*>')

    """ Just formats the tags and adds a > to the elements that don't have it """
    @staticmethod
    def _add_closing_symbol(tag_list):
        # since the regex finds either tags but not attributes, some elements might have just the <a part,
        # so add the > if needed (such as <a href=...)
        for i, t in enumerate(tag_list):
            if t[-1] != '>':
                tag_list[i] = t + '>'
        return tag_list

    """ Counts the parent divs, if there is a <div><a></a><p>hello</p>, only parents would be <div><p>, return 2 """
    @staticmethod
    def _count_parent_tags(tag_list):
        parent_counter = 0
        for i, t in enumerate(tag_list):
            if '/' not in t:
                parent_counter += 1
            else:
                parent_counter -= 1
        return parent_counter

    """ This function uses other class functions to find the xpath of potential names
     returns the xpath as far as some threshold % of all the found xpaths """
    def _find_all_xpaths(self, hxs):
        # Gets the body (including html tags) and body_text (no tags), whatever gets found should be in both, since a
        # name should be visible
        body = hxs.select('//body').extract()

        potential_names = []

        body = (body[0].encode('ascii', 'ignore')).strip()
        # keep the tags but remove the tag attributes such as name and class
        body = re.sub(self._remove_attributes, r'<\1>', body)

        # find the paired tags, remove the ones that don't have a pair such as <input>
        all_paired_tags = list(set(re.findall(self._tag, body)))
        all_paired_tags = self._add_closing_symbol(all_paired_tags)
        all_paired_tags = self._remove_unpaired_tags(all_paired_tags)

        # Get literally just the text, so when checking each element, it won't grab any tags
        no_tags = (re.sub(r'<.*?>', '', body)).splitlines()
        no_tags = ' '.join(no_tags)

        xpaths = []
        for item in no_tags.split():

            if (item in self._titles or item in self._names) and item in body:
                potential_names.append(item)
                tags = re.findall(self._tag, body[:body.index(item)])
                tags = self._add_closing_symbol(tags)

                # this part is to check if there's a tag that does not close or doesn't have an open tag (such as </br>)
                # remove the tags that don't have a match
                check_tags = list(set(tags))
                for t in check_tags:
                    if '/' not in t and (t[0] + '/' + t[1:]) not in all_paired_tags:
                        tags = [x for x in tags if x != t]
                    elif '/' in t and (t[0] + t[2:]) not in all_paired_tags:
                        tags = [x for x in tags if x != t]

                parent_counter = self._count_parent_tags(tags)
                xpaths.append(self._find_xpath(tags, parent_counter))

        xpaths = list(set(xpaths))
        return xpaths

    """ Returns one 'xpath' string """
    @staticmethod
    def _find_xpath(tag_list, parent_counter):
        i = 0
        while i < parent_counter or i < len(tag_list):
            tag = tag_list[i]
            if '/' in tag:
                # remove ending tag
                tag_list.remove(tag)
                tag_list.reverse()
                try:
                    index = tag_list[len(tag_list)-i:].index(tag[0] + tag[2:])
                    tag_list.reverse()
                    tag_list.pop(index + i - 1)
                except ValueError:
                    pass
                i -= 1
            else:
                i += 1

        tag_list = tag_list[:parent_counter+3]

        s = ''.join(tag_list)
        s = s.replace('<', '')
        s = s.replace('>', '/')
        s = '//' + s
        s += 'text()'

        return s

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        xpaths = self._find_all_xpaths(hxs)

        names_list = []
        for xpath in xpaths:
            names_list.append(hxs.select(xpath).extract())

        # check which xpath has the most names
        # if the xpath has at least 4 valid names (maybe change this in the future somehow?),
        # then keep it, otherwise it may be catching a wrong thing
        highest = []
        for i, checker in enumerate(names_list):
            count = 0
            for name in checker:
                if name.strip():
                    # Maybe change the below too? If the name is a link's text, then it will catch other links text,
                    # which can be a sentence, so assume a certain amount of words for a name? In this case 5 or less
                    if len(name.split()) > 5:
                        names_list[i].remove(name)
                        continue
                    first = (name.encode('ascii', 'ignore')).split()[0]
                    first = first.translate(string.maketrans('', ''), string.punctuation)
                    if first != [] and (first in self._names or first in self._titles):
                        count += 1
            if count > 3:
                highest.append(i)

        names = []
        for i in highest:
            for j in range(len(names_list[i])):
                names_list[i][j] = names_list[i][j].encode('ascii', 'ignore').strip()
            names += names_list[i]
        names = filter(bool, names)

        items = []
        for i in range(len(names)):
            item = ScrapedContactName()
            item['name'] = names[i]
            items.append(item)
        return items

    """ Take out the tags that don't have an ending tag, such as <input> """
    @staticmethod
    def _remove_unpaired_tags(tag_list):
        # this part is to check if there's a tag that does not close or doesn't have an open tag (such as </br>)
        # remove the tags that don't have a match
        for t in tag_list:
            if '/' not in t and (t[0] + '/' + t[1:]) not in tag_list:
                tag_list = [x for x in tag_list if x != t]
            elif '/' in t and (t[0] + t[2:]) not in tag_list:
                tag_list = [x for x in tag_list if x != t]
        return tag_list


class MockContactPositionScraper:

    def __init__(self):
        self.position = ""


class MockContactPublicationsScraper:

    def __init__(self):
        self.publications = []


class MockEmailScraper(object):
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

        emails = body+hrefs

        # Take out the unicode or whatever, and substitute [at] for @ and [dot] for .
        for i in range(len(emails)):
            emails[i] = emails[i].encode('ascii', 'ignore')
            emails[i] = re.sub(r'(\[at]|\(at\)| at )([A-Za-z0-9.-]+)(\[dot]|\(dot\)| dot )', r'@\2.', emails[i])

        # Makes it a set then back to a list to take out duplicates that may have been both in the body and links
        emails = list(set(emails))

        return emails


class MockIndianPhoneNumberScraper(object):
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


class MockKeywordScraper(object):
    NUM_KEYWORDS = 50
    _stopwords = []
    _lemmatizer = WordNetLemmatizer()

    def __init__(self):
        #Load words to be ignored
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../WebCrawler/WebCrawler/Resources/stopwords.txt')) as f:
            self._stopwords = f.read().splitlines()

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
                        append_to.append(self._lemmatizer.lemmatize(word))

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

        #Remove ignored words
        for word in self._stopwords:
            if word in freq_dist:
                del freq_dist[word]

        # Take the NUM_KEYWORDS most frequent keywords
        most_freq_keywords = dict(sorted(freq_dist.iteritems(), key=operator.itemgetter(1), reverse=True)[:self.NUM_KEYWORDS])
        return most_freq_keywords


class MockOrgAddressScraper(object):
    def __init__(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               '../../WebCrawler/WebCrawler/Resources/cities.txt')) as f:
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
        # the database is expecting a single string, so I'm going to just return first for now -Paul-
        return address_list[0]['city'] + " " + address_list[0]['zip_code'] if len(address_list) > 0 else ''


class MockOrgContactsScraper(object):

    def __init__(self):
        pass

    def parse(self, response):
        return [] # not yet implemented


class MockOrgFacebookScraper(object):

    def __init__(self):
        regex_allow = re.compile("^(?:(?:http|https)://)?(?:www\.)?facebook\.com/.+(?:/)?$", re.IGNORECASE)
        self.fb_link_ext = SgmlLinkExtractor(allow=regex_allow, canonicalize=False, unique=True)

    def parse(self, response):
        fb_links = self.fb_link_ext.extract_links(response)
        urls = [x.url for x in fb_links]
        if len(fb_links) > 0:
            return urls[0]
        return None


class MockOrgTwitterScraper(object):

    def __init__(self):
        regex_allow = re.compile("^(?:(?:http|https)://)?(?:www\.)?twitter\.com/(?:#!/)?\w+(?:/)?$", re.IGNORECASE)
        self.tw_link_ext = SgmlLinkExtractor(allow=regex_allow, canonicalize=False)

    def parse(self, response):
        tw_links = self.tw_link_ext.extract_links(response)
        urls = [x.url for x in tw_links]
        if len(urls) > 0:
            return urls[0]
        return None


class MockOrgNameScraper(object):

    def __init__(self):
        self._split_punctuation = re.compile(r"[ \w']+")
        #Load words to be ignored
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               '../../WebCrawler/WebCrawler/Resources/stopwords.txt')) as f:
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


class MockOrgPartnersScraper(object):

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
            found = hxs.select("//%s[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'partner')]" % e)
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
                    partner['organization_url'] = '%s://%s/' % (link_url.scheme, link_url.netloc)
                    partners.append(partner)

        return partners


class MockOrgTypeScraper(object):

    def __init__(self):
        # Lemmatizer for shortening each word to a more-commonly-used form of the word
        self._lemmatizer = WordNetLemmatizer()
        # Scraper to get common keywords from response
        self._keyword_scraper = MockKeywordScraper()
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

        # Get keywords
        keywords = list(self._lemmatizer.lemmatize(word) for word in self._keyword_scraper.parse(response))

        # Get all words
        all_words = []
        hxs = HtmlXPathSelector(response)
        elements = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'a', 'b', 'code', 'em', 'italic',
                    'small', 'strong', 'div', 'span', 'li', 'th', 'td', 'a[contains(@href, "image")]']
        for element in elements:
            words = hxs.select('//'+element+'/text()').extract()
            self._keyword_scraper.append_words(all_words, words)

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


class MockOrgUrlScraper(object):

    def __init__(self):
        pass

    def parse(self, response):
        parse = urlparse(response.url)
        urls = [
            '%s/' % (parse.netloc),
        ]
        return urls


class MockPublicationAuthorsScraper:

    def __init__(self):
        authors = []


class MockPublicationDateScraper:

    def __init__(self):
        partners = []


class MockPublicationPublisherScraper:

    def __init__(self):
        publisher = []


class MockPublicationTitleScraper:

    def __init__(self):
        titles = []


class MockPublicationTypeScraper:

    def __init__(self):
        type = []


class MockUrlMetadataScraper(object):

    def __init__(self):
        pass

    def parse(self, response):
        # Initialize the DAO context
        dao = MockURLMetadataDAO()

        # Initialize item and set url
        metadata = ScrapedUrl()
        metadata['url'] = response.url
        metadata['last_visited'] = datetime.now()

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
        exist_url_dto = dao.find(url=response.url)
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


class MockUSPhoneNumberScraper(object):

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
