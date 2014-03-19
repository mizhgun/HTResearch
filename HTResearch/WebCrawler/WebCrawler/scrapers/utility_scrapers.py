# stdlib imports
from bson.binary import Binary
import datetime
import hashlib
import heapq
import itertools
import os
import re
import string
from nltk import FreqDist, WordNetLemmatizer
from scrapy.selector import HtmlXPathSelector
from scrapy.selector import XPathSelectorList
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from sgmllib import SGMLParseError
from urlparse import urlparse, urljoin

# project imports
from ..items import *
from link_scraper import LinkScraper
from HTResearch.DataAccess.dao import *
from HTResearch.DataModel.enums import OrgTypesEnum
from HTResearch.Utilities.converter import *
from HTResearch.Utilities.logutil import *

#region Globals
_utilityscrapers_logger = get_logger(LoggingSection.CRAWLER, __name__)
#endregion


class ContactNameScraper(object):
    """
    Scrapes first and last names of people on a given page.

    Attributes:
        _names (list of str): First names to look for on the page.
        _last_names (list of str): Last names to look for on the page.
        _stopwords (list of str): Words that will be ignored and won't count as names.
        _titles (list of str): Different titles a person can have.
        _date (regex obj): Regex to check if a potential name is a date.
    """
    try:
        _names and _last_names and _stopwords and _titles
    except NameError:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../Resources/names.txt'), 'r') as f:
            names = f.read().splitlines()
            _names = [name.title() for name in names]
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../Resources/lastnames.txt'), 'r') as f:
            lnames = f.read().splitlines()
            _last_names = [lname.title() for lname in lnames]
        #Load words to be ignored
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../Resources/stopwords.txt')) as f:
            stopwords = f.read().splitlines()
            _stopwords = [word.title() for word in stopwords]

        _titles = ['Mr', 'Mrs', 'Ms', 'Miss', 'Dr', 'Sh', 'Smt', 'Prof', 'Shri']
        length = len(_titles)
        # catch Dr and Dr.
        for i in range(0, length):
            _titles.append(_titles[i] + '.')

    def __init__(self):
        # Make a regex check for if a potential name is actually a date. Not concerned with months that aren't in the
        # names list
        self._date = re.compile(r'Jan ([0-9]{4}|[0-9]{1,2}|[0-9]{1,2}(rd|th|nd)?)|'
                                r'April ([0-9]{4}|[0-9]{1,2}|[0-9]{1,2}(rd|th|nd)?)|'
                                r'May ([0-9]{4}|[0-9]{1,2}|[0-9]{1,2}(rd|th|nd)?)|'
                                r'June ([0-9]{4}|[0-9]{1,2}|[0-9]{1,2}(rd|th|nd)?)|'
                                r'August ([0-9]{4}|[0-9]{1,2}|[0-9]{1,2}(rd|th|nd)?)')

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        body = hxs.select('//body//text()').extract()
        body = [s.strip() for s in body if s.strip()]
        names = []
        cns = ContactNameScraper

        for s in body:
            str_split = s.split()
            length = len(str_split) - 1
            name_to_add = ""
            # start at the back of string to get last name and then get all previous names
            for i in range(length, -1, -1):
                split_index = str_split[i]

                # variables for below elif to not be so terrifying
                stop_word = split_index not in cns._stopwords or len(split_index) == 1
                uppercase = split_index.istitle() or split_index.isupper()
                all_alpha = all(c.isalpha() or c == '.' for c in split_index)
                date = re.match(self._date, split_index)

                # if it's in the last names and it isn't the first word in the string
                if split_index in cns._last_names and split_index != str_split[0] and not date:
                    name_to_add = split_index + " " + name_to_add

                # if in first names
                elif split_index in cns._names and not date:
                    name_to_add = split_index + " " + name_to_add

                    # if the last name wasn't caught but first name was and next word is last name format
                    try:
                        next_uppercase = str_split[i + 1].istitle() or str_split[i + 1].isupper()
                        next_all_alpha = all(c.isalpha() or c == '.' for c in str_split[i + 1])
                        if next_uppercase and str_split[i + 1] not in cns._stopwords and \
                                next_all_alpha and str_split[i + 1] not in name_to_add:
                            name_to_add += str_split[i + 1]
                    except IndexError:
                        pass

                # will catch a first name if a last name has been caught and if it's in correct name format
                elif stop_word and split_index not in cns._titles and uppercase and all_alpha and \
                        name_to_add and not date:
                    name_to_add = split_index + " " + name_to_add
                elif (not split_index.istitle() and name_to_add) or date:
                    break

            # only get names that are both first and last name
            if len(name_to_add.split()) > 1:
                names.append(name_to_add)
        names = [name.encode('ascii', 'ignore') for name in names]
        items = []
        for i in range(len(names)):
            item = ScrapedContactName()
            item['name'] = names[i].strip()
            items.append(item)
        return items


class ContactPositionScraper(object):
    """
    Scrapes work positions of people on a given page.

    Attributes:
        _positions (list of str): Professional positions that people may have.
        _tag (regex obj): Regex to find html tags on a page.
    """
    def __init__(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../Resources/positions.txt')) as f:
            self._positions = f.read().splitlines()
        self._tag = re.compile(r'<[A-Za-z0-9]*>|<[A-Za-z0-9]+|</[A-Za-z0-9]*>')

    def parse(self, response):
        for position in self._positions:
            if string.find(response.body, position) is not -1:
                return position


class EmailScraper(object):
    """
    Scrapes emails on a given page.

    Attributes:
        _email_regex (regex obj): Regex to find all the different email formats.
        _c_data (regex obj): C data on a page generally could be found as an email format,
                             so catch it and don't count it as an email.
    """
    def __init__(self):
        self._email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+\[at][A-Za-z0-9.-]+\[dot][A-Za-z]{2,4}\b|'
                                       r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}\b|'
                                       r'\b[A-Za-z0-9._%+-]+ at [A-Za-z0-9.-]+ dot [A-Za-z]{2,4}\b|'
                                       r'\b[A-Za-z0-9._%+-]+\(at\)[A-Za-z0-9.-]+\(dot\)[A-Za-z]{2,4}\b')
        self._c_data = re.compile(r'(.*?)<!\[CDATA(.*?)]]>(.*?)', re.DOTALL)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        # body will get emails that are just text in the body
        body = hxs.select('//body//text()')

        # Remove C_Data tags, since they are showing up in the body text for some reason
        body = XPathSelectorList([text for text in body if not (re.match(self._c_data, text.extract()) or
                                                                text.extract().strip() == '')])

        body = body.re(self._email_regex)

        # hrefs will get emails from hrefs
        hrefs = hxs.select("//./a[contains(@href,'@')]/@href").re(self._email_regex)

        emails = body + hrefs

        # Take out the unicode, and substitute [at] for @ and [dot] for .
        for i in range(len(emails)):
            emails[i] = emails[i].encode('ascii', 'ignore')
            emails[i] = re.sub(r'(\[at]|\(at\)| at )([A-Za-z0-9.-]+)(\[dot]|\(dot\)| dot )', r'@\2.', emails[i])

        # Makes it a set then back to a list to take out duplicates that may have been both in the body and links
        emails = list(set(emails))

        return emails


class KeywordScraper(object):
    """
    Scrapes the 50 most used words on a given page.

    Attributes:
        _stopwords (list of str): Excluding words as keywords if they are in stopwords.txt.
    """
    NUM_KEYWORDS = 50
    _stopwords = []
    _lemmatizer = WordNetLemmatizer()

    def __init__(self):
        #Load words to be ignored
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../Resources/stopwords.txt')) as f:
            self._stopwords = f.read().splitlines()

    def format_extracted_text(self, list):
        """
        Removes the unicode encoding of the list of keywords.

        Arguments:
            list (list of str): List of keywords that were scraped.

        Returns:
            list (list of str): List of keywords without unicode.
        """
        for i in range(len(list)):
            list[i] = list[i].encode('ascii', 'ignore')
        return list

    def append_words(self, append_to, source):
        """
        Get all the words from the page by removing punctuation and digits.

        Arguments:
            append_to (list of str): The list of the words that have been scraped at the time.
            source (list of str): The text from the page to be scraped.

        Returns:
            append_to (list of str): List of all words that have been scraped thus far.
        """
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
        most_freq_keywords = heapq.nlargest(self.NUM_KEYWORDS, freq_dist, key=freq_dist.get)
        return ' '.join(most_freq_keywords)


class IndianPhoneNumberScraper(object):
    """
    Scrapes Indian phone numbers on a given page.

    Attributes:
        _india_format_regex (regex obj): Regex to catch the formats of Indian phone number formats.
    """
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
            phone_nums_list.append(num)

        return phone_nums_list


class OrgAddressScraper(object):
    """
    Scrapes the city and country of an organization on a given page.

    Attributes:
        _cities (list of str): Cities to be scraped from the page.
    """
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
    """
    Scrapes the contacts that are associated with an organization on a given page.

    Attributes:
        _name_scraper (ContactNameScraper): Scrapes the names of contacts associated with this organization.
        _number_scraper (IndianPhoneNumberScraper): Scrapes Indian phone numbers.
        _us_number_scraper (USPhoneNumberScraper): Scrapes US phone numbers.
        _email_scraper (EmailScraper): Scrapes emails.
        _position_scraper (ContactPositionScraper): Scrapes profession positions of contacts.
        _org_name_scraper (OrgNameScraper): Scrapes the organization name on its homepage.
        _contacts (list of Contact): Contains all the contacts that are found.
    """
    def __init__(self):
        self._name_scraper = ContactNameScraper()
        self._number_scraper = IndianPhoneNumberScraper()
        self._us_number_scraper = USPhoneNumberScraper()
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
                n = string.find(response.body, name.get('name'))    # find the index of each contact so we can search
                contact_indices.append(n)                           # only between the contacts for their info
        for i in range(len(names)):
            if i < len(names) - 1:
                cr = response.replace(body=response.body[contact_indices[i]:contact_indices[i + 1]])
            else:
                cr = response.replace(body=response.body[contact_indices[i]:])
            self._contacts[names[i].get('name')]['position'] = [self._position_scraper.parse(cr)
                                                                if self._position_scraper.parse(cr)
                                                                else None][0]
            india_num = self._number_scraper.parse(cr)[0] if self._number_scraper.parse(cr) else None
            if india_num:
                numbers = [india_num]
            else:
                us_num = self._us_number_scraper.parse(cr)[0] if self._us_number_scraper.parse(cr) else None
                if us_num:
                    numbers = [us_num]
                else:
                    numbers = []
            self._contacts[names[i].get('name')]['number'] = numbers
            self._contacts[names[i].get('name')]['email'] = [self.compare_emails(cr, names[i].get('name'))
                                                             if self.compare_emails(cr, names[i].get('name'))
                                                             else None][0]
            self._contacts[names[i].get('name')]['organization'] = org_name
        return self._contacts

    # if any part of the name is in the email, take that email, otherwise just take the first element from the list
    def compare_emails(self, response, name):
        """
        Checks if the contact's name is in an email to try and get the correct one.

        Arguments:
            response (Response): The page to scrape for emails.
            name (str): Name of the contact.

        Returns:
            If name is in one of the emails, return that email.
            Else return first email in the list.
            If no emails in the list, return None.
        """
        emails = self._email_scraper.parse(response)
        name_split = name.split()
        for email in emails:
            for split_index in name_split:
                if split_index.lower() in email.lower():
                    return email
        if emails:
            return emails[0]
        return None


class OrgFacebookScraper(object):
    """
    Scrapes an organization's Facebook link on a given page

    Attributes:
        _fb_link_ext (SgmlLinkExtractor): Scrapes the Facebook link.
    """
    def __init__(self):
        regex_allow = re.compile("^(?:(?:http|https)://)?(?:www\.)?facebook\.com/.+(?:/)?$", re.IGNORECASE)
        self._fb_link_ext = SgmlLinkExtractor(allow=regex_allow, canonicalize=False, unique=True)

    def parse(self, response):
        try:
            fb_links = self._fb_link_ext.extract_links(response)
        except SGMLParseError as e:
            # Page was poorly formatted, oh well
            _utilityscrapers_logger.error('Exception encountered when link extracting page: %s' % str(response.url))
            return None

        urls = [x.url for x in fb_links]
        if len(fb_links) > 0:
            return urls[0]
        return None


class OrgTwitterScraper(object):
    """
    Scrapes an organization's Twitter link on a given page.

    Attributes:
        _tw_link_ext (SgmlLinkExtractor): Scrapes the Twitter link.
    """
    def __init__(self):
        regex_allow = re.compile("^(?:(?:http|https)://)?(?:www\.)?twitter\.com/(?:#!/)?\w+(?:/)?$", re.IGNORECASE)
        self._tw_link_ext = SgmlLinkExtractor(allow=regex_allow, canonicalize=False, unique=True)

    def parse(self, response):
        try:
            tw_links = self._tw_link_ext.extract_links(response)
        except SGMLParseError as e:
            # Page was poorly formatted, oh well
            _utilityscrapers_logger.error('Exception encountered when link extracting page: %s' % str(response.url))
            return None

        urls = [x.url for x in tw_links]
        if len(urls) > 0:
            return urls[0]
        return None


class OrgNameScraper(object):
    """
    Scrapes the organization name on a given page.

    Attributes:
        _split_punctuation (regex obj): Regex to split the title tag based on punctuation
        _stopwords (list of str): Words to be ignored
    """
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
    """
    Scrapes partner organizations of a particular organization on a given page.

    Attributes:
        _link_scraper (LinkScraper): Scrapes the links on the page.
        _partner_text (str): Text to determine if the page has partners on it.
        _blocked_domains (list of str): List of urls that are common but not related to human trafficking.
                                        Ex: CNN
    """
    def __init__(self):
        self._link_scraper = LinkScraper()
        self._partner_text = 'partner'
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               '../Resources/blocked_org_domains.txt')) as f:
            self._blocked_domains = map(lambda x: x.rstrip(), f)

    def _path_to(self, sel):
        """
        Find the path to selected node(s)

        Arguments:
            sel (list of XPathSelector):

        Returns:
            path (str): XPath to the partner organization's link
        """
        path = ''
        while sel:
            tags = sel.select('name()').extract()
            path = '/%s%s' % (tags[0], path)
            sel = sel.select('..')
        return path

    def _external_link_count(self, page_url, sel):
        """
        Find out how many external links are in a list

        Arguments:
            page_url (str): Url of the page
            sel ():

        Returns:
            count (int): Number of links in
                         Returns 0 if not all external links
        """
        count = 0
        checked_domains = []
        for href in sel.select('@href').extract():
            link_url = urlparse(urljoin(page_url.geturl(), href))
            # link is external
            if link_url.netloc != page_url.netloc:
                # link is not to a blocked domain
                if not any(link_url.netloc.endswith(domain) for domain in self._blocked_domains):
                    checked_domains.append(link_url.netloc)
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
                if link_url.netloc not in self._blocked_domains + [page_url.netloc]:
                    partner = ScrapedOrganization()
                    partner['organization_url'] = '%s/' % link_url.netloc
                    partners.append(partner)

        return partners


class OrgTypeScraper(object):
    """
    Scrapes the type of an organization based on keywords that were scraped.

    Attributes:
        _lemmatizer (WordNetLemmatizer):
        _keyword_scraper (KeywordScraper): KeywordScraper to check the words.
        _max_types (int): Maximum number of types an organization can have.
        _religion_words (list of str): Words that associate with religious organizations.
        _government_detector (regex str): Checks for a gov domain in the url.
        _max_rank (int): Lowest rank that a keyword can have and still be a type for an organization. -unused for now
        _type_words (enum): Enum with keys being the keyword with a list value of the words associated to that type.
    """
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
                'avoidance',
                'blockage',
                'determent',
                'forestalling',
                'halt',
                'hindrance',
                'impediment',
                'inhibitor',
                'interception',
                'interruption',
                'obstacle',
                'obstruction',
                'prohibition',
                'stoppage',
                'thwarting',
                'deterence',
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
                'conservation',
                'insurance',
                'preservation',
                'safeguard',
                'safety',
                'security',
                'shelter',
                'stability',
                'assurance',
                'barrier',
                'cover',
                'custody',
                'defense',
                'fix',
                'guard',
                'invulnerability',
                'reassurance',
                'refuge',
                'safekeeping',
                'salvation',
                'screen',
                'self-defense',
                'shield',
                'strength',
                'surety',
                'guarding',
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
                'case',
                'cause',
                'claim',
                'lawsuit',
                'litigation',
                'proceeding',
                'suit',
            ],
        }

        # Stem search words (religious, general)
        self._religion_words = [self._lemmatizer.lemmatize(word) for word in self._religion_words]
        for key in self._type_words.iterkeys():
            self._type_words[key] = [self._lemmatizer.lemmatize(word) for word in self._type_words[key]]

    # UNUSED FUNCTION?
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
        keyword_string = keyword_scraper_inst.parse(response)
        keywords = keyword_string.split()

        # Get all words
        all_words = []
        hxs = HtmlXPathSelector(response)
        elements = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'a', 'b', 'code', 'em', 'italic',
                    'small', 'strong', 'div', 'span', 'li', 'th', 'td', 'a[contains(@href, "image")]']
        for element in elements:
            words = hxs.select('//' + element + '/text()').extract()
            keyword_scraper_inst.append_words(all_words, words)

        all_words = list(set(self._lemmatizer.lemmatize(word) for word in all_words))

        threepees = False
        types = []
        # Government: check the URL
        if re.search(self._government_detector, urlparse(response.url).netloc):
            types.append(OrgTypesEnum.GOVERNMENT)
        # Religion: check for the appearance of certain religious terms
        # (this means that government and religion types are mutually exclusive)
        elif any(word in self._religion_words for word in all_words):
            types.append(OrgTypesEnum.RELIGIOUS)
            # Other types

        for word in keywords:
        #go through keywords in order of frequency, checking if they associate with one of our types
            for type in self._type_words.iterkeys():
                if word in self._type_words[type]:
                    types.append(type)
                    if type == OrgTypesEnum.PREVENTION or type == OrgTypesEnum.PROTECTION or type == OrgTypesEnum.PROSECUTION:
                        threepees = True
                    #uniquify
                    types = list(set(types))
                    break
                if len(types) >= self._max_types:
                    #if there are three types but none of them are P's, replace the last one with prevention
                    if not threepees:
                        types[self._max_types] = OrgTypesEnum.PREVENTION
                        threepees = True
                    break
        #if there are less than three types and none of them are P's, append prevention
        if not threepees:
            types.append(OrgTypesEnum.PREVENTION)
        return types or [OrgTypesEnum.UNKNOWN]


class OrgUrlScraper(object):
    """
    Scrapes the url of an organization on a given page.

    Attributes:
        None
    """
    def __init__(self):
        pass

    def parse(self, response):
        parse = urlparse(response.url)
        url = '%s/' % parse.netloc
        return url


class PublicationCitationSourceScraper(object):
    """
    Scrapes the sources of a publication.

    Attributes:
        hash_regex (regex obj):
    """
    def __init__(self):
        self.hash_regex = re.compile('\w{12}')

    def parse(self, response):
        #All hashes are fetched by gs_ocit calls
        source_string_regex = re.compile("return gs_ocit\(event,'\w{12}'")
        keys = []
        hxs = HtmlXPathSelector(response)
        #Currently, Google Scholar has it so we only need to parse 'a' elements
        #for the ajax source keys
        sources = hxs.select('//a').re(source_string_regex)
        for source in sources:
            keys.append(re.search(self.hash_regex, source).group())

        return keys


class PublicationAuthorsScraper(object):
    """
    Scrapes the author(s) of a publication.

    Attributes:
        None
    """
    def __init__(self):
        pass

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        #Each citation request will always only have one matched selection
        #And it is returned as a unicode value, so we must convert it
        chicago_format_html = hxs.select('//div[@id=\'gs_cit2\']').extract()[0].encode('ascii', 'ignore')
        chicago_format_html = str.replace(chicago_format_html, '<div id="gs_cit2" tabindex="0" class="gs_citr">', '')
        chicago_format_html = str.replace(chicago_format_html, '</div>', '')

        author_delim = ' <i>' if chicago_format_html.find('<i>') < chicago_format_html.find('\"') else '\"'

        if not author_delim in chicago_format_html:
            author_delim = ' <i>'

        author_str = chicago_format_html.split(author_delim)[0]

        return author_str


class PublicationDateScraper(object):
    """
    Scrapes the date of a publication.

    Attributes:
        date_regex (regex obj):
    """
    def __init__(self):
        self.date_regex = re.compile('\d{4}')

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        #Each citation request will always only have one matched selection
        #And it is returned as a unicode value, so we must convert it
        chicago_format_html = hxs.select('//div[@id=\'gs_cit2\']').extract()[0].encode('ascii', 'ignore')
        chicago_format_html = str.replace(chicago_format_html, '<div id="gs_cit2" tabindex="0" class="gs_citr">', '')
        chicago_format_html = str.replace(chicago_format_html, '</div>', '')

        date = re.search(self.date_regex, chicago_format_html).group()
        return date


class PublicationPublisherScraper(object):
    """
    Scrapes the publisher of a citation.

    Attributes:
        None
    """
    def __init__(self):
        pass

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        #Each citation request will always only have one matched selection
        #And it is returned as a unicode value, so we must convert it
        chicago_format_html = hxs.select('//div[@id=\'gs_cit2\']').extract()[0].encode('ascii', 'ignore')
        chicago_format_html = str.replace(chicago_format_html, '<div id="gs_cit2" tabindex="0" class="gs_citr">', '')
        chicago_format_html = str.replace(chicago_format_html, '</div>', '')

        start_delim = '</i>. ' if chicago_format_html.find('<i>') < chicago_format_html.find('\"') else '.\" <i>'
        end_delim = ',' if start_delim == '</i>. ' else '</i>'
        if not start_delim in chicago_format_html:
            start_delim = '</i>. '
            end_delim = ','

        start_index = chicago_format_html.find(start_delim) + len(start_delim)

        publisher = chicago_format_html[start_index:chicago_format_html.rfind(end_delim)]

        return publisher


class PublicationTitleScraper(object):
    """
    Scrapes the title of a publication.

    Attributes:
        None
    """
    def __init__(self):
        pass

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        #Each citation request will always only have one matched selection
        #And it is returned as a unicode value, so we must convert it
        chicago_format_html = hxs.select('//div[@id=\'gs_cit2\']').extract()[0].encode('ascii', 'ignore')
        chicago_format_html = str.replace(chicago_format_html, '<div id="gs_cit2" tabindex="0" class="gs_citr">', '')
        chicago_format_html = str.replace(chicago_format_html, '</div>', '')

        title_delim = ' <i>' if chicago_format_html.find('<i>') < chicago_format_html.find('\"') else ' \"'
        ending_title_delim = '</i>' if title_delim == ' <i>' else ".\" "

        if not title_delim in chicago_format_html:
            title_delim = ' <i>'
            ending_title_delim = '</i>'

        #This parses the title out of the string
        title = chicago_format_html[chicago_format_html.find(title_delim) + len(title_delim)
                                    :chicago_format_html.find(ending_title_delim)]

        return title


class PublicationURLScraper(object):
    """
    Scrapes the url of a publication.

    Attributes:
        titles (list of str): Contains titles of publications.
    """
    def __init__(self):
        #Seed titles to look for on page
        self.titles = []

    def seed_titles(self, title_names):
        self.titles = self.titles + title_names

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        sources = hxs.select('//h3/a').extract()

        urls = []
        for i in range(0, len(self.titles)):
            urls.append(None)

        start = "=\""
        index = 0
        for title in self.titles:
            for source in sources:
                    if re.sub(r'\W+', '', title) in re.sub(r'\W+', '', source):
                        raw_link = source.encode('ascii', 'ignore')
                        urls[index] = raw_link[raw_link.find(start) + len(start):raw_link.find("\">")]
            index += 1
        return urls


class UrlMetadataScraper(object):
    """
    Scrapes the metadata of a particular url.

    Attributes:
        dao (URLMetadataDAO): DAO object to check if the url exists in DB already.
    """
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

        return metadata


class USPhoneNumberScraper(object):
    """
    Scrapes US phone numbers on a given page

    Attributes:
        None
    """
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
            phone_nums_list.append(num)

        return phone_nums_list


def flatten(l):
    # Flatten one level of nesting
    return itertools.chain.from_iterable(l)
