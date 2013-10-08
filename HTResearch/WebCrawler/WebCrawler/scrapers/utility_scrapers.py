from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
from webcrawler.items import *
import pdb
import re
from nltk import FreqDist
import os
import string

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

class KeywordScraper:

    def __init__(self):
        #Add path
        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)
        os.chdir(dname)

        #Load words to be ignored
        with open("stopwords.txt") as f:
            stopwords = f.readlines()
        for i in range(len(stopwords)):
            stopwords[i] = stopwords[i].strip()

    def format_extracted_text(self, list):

        for i in range(len(list)):
            list[i] = list[i].encode('ascii','ignore')
        return list
            
    def append_words(self, append_to, source):
        if source == []:
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
        num_keywords_to_return = 50
        all_words = []

        #Parse the response
        hxs = HtmlXPathSelector(response)

        ##Headers
        h1=hxs.select('//h1/text()').extract()
        all_words = self.append_words(all_words, h1)
        h2=hxs.select('//h2/text()').extract()
        all_words = self.append_words(all_words, h2)
        h3=hxs.select('//h3/text()').extract()
        all_words = self.append_words(all_words, h3)
        h4=hxs.select('//h4/text()').extract()
        all_words = self.append_words(all_words, h4)
        h5=hxs.select('//h5/text()').extract()
        all_words = self.append_words(all_words, h5)
        h6=hxs.select('//h6/text()').extract()
        all_words = self.append_words(all_words, h6)

        p = hxs.select('//p/text()').extract()
        all_words = self.append_words(all_words, p)

        a = hxs.select('//a/text()').extract()
        all_words = self.append_words(all_words, a)

        b = hxs.select('//b/text()').extract()
        all_words = self.append_words(all_words, b)

        code = hxs.select('//code/text()').extract()
        all_words = self.append_words(all_words, code)

        em = hxs.select('//em/text()').extract()
        all_words = self.append_words(all_words, em)

        italic = hxs.select('//i/text()').extract()
        all_words = self.append_words(all_words, italic)

        small = hxs.select('//small/text()').extract()
        all_words = self.append_words(all_words, small)

        strong = hxs.select('//strong/text()').extract()
        all_words = self.append_words(all_words, strong)

        div =  hxs.select('//div/text()').extract()
        all_words = self.append_words(all_words, div)

        span = hxs.select('//span/text()').extract()
        all_words = self.append_words(all_words, span)

        li = hxs.select('//li/text()').extract()
        all_words = self.append_words(all_words, li)

        th = hxs.select('//th/text()').extract()
        all_words = self.append_words(all_words, th)

        td = hxs.select('//td/text()').extract()
        all_words = self.append_words(all_words, td)

        href = hxs.select('//a[contains(@href, "image")]/text()').extract()
        all_words = self.append_words(all_words, href)

        #Run a frequency distribution on the web page body
        freq_dist = FreqDist(all_words)

        #Parse the distribution into individual words without frequencies
        keywords = freq_dist.keys()

        #Remove ignored words
        parsed_keywords = [word for word in keywords if word not in stopwords]
        
        #Sort by frequency
        most_freq_keywords = parsed_keywords[:num_keywords_to_return]
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
