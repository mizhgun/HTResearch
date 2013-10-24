from scrapy.selector import HtmlXPathSelector
from ..items import *
import itertools
import os
from nltk import FreqDist
import nltk
import pdb
import re
import string

# ALL OF THE TEMPLATE CONSTRUCTORS ARE JUST THERE SO THERE ARE NO ERRORS WHEN TESTING THE SCRAPERS THAT ARE DONE.
# Will likely remove/change them.


class ContactNameScraper:

    def __init__(self):
        self.saved_path = os.getcwd()
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        with open("../Resources/names.txt") as f:
            self.names = f.read().splitlines()
        self.titles = ['Mr', 'Mrs', 'Ms', 'Miss', 'Dr']
        self.tag = re.compile(r'<[A-Za-z0-9]*>|<[A-Za-z0-9]+|</[A-Za-z0-9]*>')

    def __del__(self):
        os.chdir(self.saved_path)

    """ Just formats the tags and adds a > to the elements that don't have it """
    @staticmethod
    def add_closing_symbol(tag_list):
        # since the regex finds either tags but not attributes, some elements might have just the <a part,
        # so add the > if needed (such as <a href=...)
        for i, t in enumerate(tag_list):
            if t[-1] != '>':
                tag_list[i] = t + '>'
        return tag_list

    """ Counts the parent divs, if there is a <div><a></a><p>hello</p>, only parents would be <div><p>, return 2 """
    @staticmethod
    def count_parent_tags(tag_list):
        parent_counter = 0
        for i, t in enumerate(tag_list):
            if '/' not in t:
                parent_counter += 1
            else:
                parent_counter -= 1
        return parent_counter

    """ This function uses other class functions to find the xpath of potential names
     returns the xpath as far as some threshold % of all the found xpaths """
    def find_all_xpaths(self, hxs):
        # Gets the body (including html tags) and body_text (no tags), whatever gets found should be in both, since a
        # name should be visible
        body = hxs.select('//body').extract()

        body_text = hxs.select('//body//text()').extract()
        for i in range(len(body_text)):
            body_text[i] = (body_text[i].encode('ascii', 'ignore')).strip()
        body_text = filter(bool, body_text)
        body_text = ' '.join(body_text)

        potential_names = []

        body = (body[0].encode('ascii', 'ignore')).strip()
        # keep the tags but remove the tag attributes such as name and class
        body = re.sub(r'<([A-Za-z][A-Za-z0-9]*)[^>]*>', r'<\1>', body)

        # find the paired tags, remove the ones that don't have a pair such as <input>
        all_paired_tags = list(set(re.findall(self.tag, body)))
        all_paired_tags = self.add_closing_symbol(all_paired_tags)
        all_paired_tags = self.remove_unpaired_tags(all_paired_tags)

        # Get literally just the text, so when checking each element, it won't grab any tags
        no_tags = (re.sub(r'<.*?>', '', body)).splitlines()
        no_tags = ' '.join(no_tags)

        xpaths = []
        for item in no_tags.split():

            if (item in self.titles or item in self.names) and item in body_text and item in body:
                #pdb.set_trace()
                potential_names.append(item)
                tags = re.findall(self.tag, body[:body.index(item)])
                tags = self.add_closing_symbol(tags)

                # this part is to check if there's a tag that does not close or doesn't have an open tag (such as </br>)
                # remove the tags that don't have a match
                check_tags = list(set(tags))
                for t in check_tags:
                    if '/' not in t and (t[0] + '/' + t[1:]) not in all_paired_tags:
                        tags = [x for x in tags if x != t]
                    elif '/' in t and (t[0] + t[2:]) not in all_paired_tags:
                        tags = [x for x in tags if x != t]

                parent_counter = self.count_parent_tags(tags)
                xpaths.append(self.find_xpath(tags, parent_counter, item, hxs))

        # go as far as 40% of the xpaths potential names
        #threshold = 0.4
        #size = len(xpaths)
        #for i in range(len(xpaths)-1):
        #    count = 0
        #    tag_split = (xpaths[i]).split('/')
        #    for j, tag in enumerate(tag_split):
        #        j = i + 1
        #        tag = tag.strip()
        #        if xpaths[i] == xpaths[j]:
        #            count += 1

        xpaths = list(set(xpaths))

        return xpaths

    """ Returns one 'xpath' string """
    @staticmethod
    def find_xpath(tag_list, parent_counter, item, hxs):
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
        # Could I confirm a name is actually a name and then grab the tag that name is in and assume that other names
        # on the page will also be in the same tags?

        hxs = HtmlXPathSelector(response)

        xpaths = self.find_all_xpaths(hxs)

        names_list = []
        for xpath in xpaths:
            names_list.append(hxs.select(xpath).extract())

        # check which xpath has the most names
        # if the xpath has at least 5 valid names, then keep it, otherwise it may be catching a wrong thing
        highest = []
        for i, checker in enumerate(names_list):
            count = 0
            for name in checker:
                if name.strip():
                    if len(name.split()) > 5:
                        names_list[i].remove(name)
                        continue
                    first = (name.encode('ascii', 'ignore')).split()[0]
                    first = first.translate(string.maketrans('', ''), string.punctuation)
                    if first != [] and (first in self.names or first in self.titles):
                        count += 1
            if count > 3:
                highest.append(i)

        names = []
        for i in highest:
            names += names_list[i]

        for i in range(len(names)):
            names[i] = (names[i].encode('ascii', 'ignore')).strip()
        names = filter(bool, names)

        return names

    """ Take out the tags that don't have an ending tag, such as <input> """
    @staticmethod
    def remove_unpaired_tags(tag_list):
        # this part is to check if there's a tag that does not close or doesn't have an open tag (such as </br>)
        # remove the tags that don't have a match
        for t in tag_list:
            if '/' not in t and (t[0] + '/' + t[1:]) not in tag_list:
                tag_list = [x for x in tag_list if x != t]
            elif '/' in t and (t[0] + t[2:]) not in tag_list:
                tag_list = [x for x in tag_list if x != t]
        return tag_list


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


class KeywordScraper:
    NUM_KEYWORDS = 50
    stopwords = []

    def __init__(self):
        self.saved_path = os.getcwd()
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        #Load words to be ignored
        with open("../Resources/stopwords.txt") as f:
            self.stopwords = f.read().splitlines()

    def __del__(self):
        os.chdir(self.saved_path)

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
        body = list(flatten(body))

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


class OrgContactsScraper:

    def __init__(self):
        self.contacts = []


class OrgNameScraper:

    def __init__(self):
        self.names = []

    def parse(self, response):
        names_list = []
        return names_list


class OrgPartnersScraper:

    def __init__(self):
        self.partners = []


class OrgTypeScraper:

    def __init__(self):
        types = []


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


def flatten(l):
    # Flatten one level of nesting
    return itertools.chain.from_iterable(l)
