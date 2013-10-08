from scrapy.selector import HtmlXPathSelector
from ..items import *
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