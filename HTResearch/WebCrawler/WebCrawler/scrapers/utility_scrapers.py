from scrapy.selector import HtmlXPathSelector
from ..items import *
import itertools
import pdb
import re

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
    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        """ THIS IS ALL FOR THE PAGE http://www.tiss.edu/TopMenuBar/contact-us/location-1 """
        #content_div = hxs.select('//div[@id="content"]')
        
        ## text will select the text before the </br> if the <p> tag has <em><strong>Postal Address</></>
        #addresses = content_div.select('./span/p[contains(./em/strong/text(),"Postal Address")]/br[1]/preceding-sibling::text()[1]').extract()

        #for i in range(len(addresses)):
        #    addresses[i] = addresses[i].encode('ascii','ignore')
        #    addresses[i] = addresses[i].strip()
        #    if (addresses[i])[len(addresses[i])-1] == ",":
        #        after_break = (content_div.select('//span/p[@align="justify"]/br[1]/following-sibling::text()[1]').extract())[0]
        #        after_break = (after_break.strip()).encode('ascii','ignore')
        #        addresses[i] = addresses[i] + " " + after_break
        #    if (addresses[i][0] == ":"):
        #        addresses[i] = (addresses[i][1:]).strip()
        #    if (addresses[i][len(addresses[i])-1] == "."):
        #        addresses[i] = (addresses[i][:-1]).strip()

        """ THIS IS ALL FOR THE PAGE http://apneaap.org/contact/ """
        #content_div = hxs.select('//div[@class="entry-content"]')

        #text = content_div.select('./p/text()').extract()
        #address = ""
        #addresses = []

        #for i in range(len(text)):
        #    text[i] = text[i].encode('ascii','ignore')
        #    text[i] = text[i].strip()
        #    if (text[i][:3] == "(T)"):
        #        addresses.append(address)
        #        address = ""
        #    else:
        #        if address != "":
        #            address += ", "
        #        address += text[i]

        """ THIS IS ALL FOR THE PAGE http://www.aawc.in/contact_us.html """
        #text = hxs.select('//address/p[contains(./img/@src,"images/add_icons.jpg")]/text()').extract()
        #address = ""
        #addresses = []
        #for i in range(len(text)):
        #    text[i] = text[i].encode('ascii','ignore')
        #    text[i] = text[i].strip()

        #    if i != 0:
        #        if text[i-1][-1] == ",":
        #            address += " " + text[i]
        #            addresses.append(address)
        #            address = ""
        #        else:
        #            address += text[i]
        #    else:
        #        address += text[i]

        """ THIS IS ALL FOR THE PAGE https://bombayteenchallenge.org/ """
        ##text = hxs.select('//div[@class="textwidget"]/p/text()[position()>1 and position()!=last()]').extract()
        #text = hxs.select('//div[@class="textwidget"]/p/text()[position()>1]').extract()
        #address = ""
        #addresses = []

        #for i in range(len(text)):
        #    text[i] = (text[i].encode('ascii','ignore')).strip()
        #    if text[i][:3] == "Tel":
        #        addresses.append(address)
        #        address = ""
        #    else:
        #        if address != "":
        #            address += ", "
        #        address += text[i]

        """ THIS IS ALL FOR THE PAGE http://www.compliance-matters.com/human-trafficking/ """
        #text = hxs.select('//footer/div[@class="col first"]/p/text()').extract()

        #addresses = []
        #for i in range(len(text)):
        #    text[i] = (text[i].encode('ascii','ignore')).strip()
        #    if (i == 0 or i == 3):
        #        find_preceding_str = text[i].find(": ")
        #        length = len(": ")
        #        text[i] = text[i][find_preceding_str+length:]
        #addresses.append(text[0] + " " + text[1] + ", " + text[2])
        #addresses.append(text[3] + ", " + text[4] + " " + text[5])

        """ THIS IS ALL FOR THE PAGE http://www.prajwalaindia.com/home.html """
        #text = hxs.select('//div[@id="footer_inner_right"]/p/text()').extract()
        #
        #addresses = []
        #for i in range(len(text)):
        #    text[i] = (text[i].encode('ascii','ignore')).strip()
        #addresses.append(", ".join(text))

        body = hxs.select('//body//text()').extract()
        for i in range(len(body)):
            body[i] = (body[i].encode('ascii', 'ignore')).strip()
            body[i] = "".join((char if char.isalnum() else " ") for char in body[i]).split()
        body = list(self.flatten(body))

        f = open("C:\Users\Brian\Documents\cities.txt", 'r')
        cities = f.read().splitlines()

        # This loop will check if city is in the body, if it is, find all occurrences of that city in the body,
        # and then it will check all the occurring indices, and if the next index (or next 2 indices) is the zip code
        city_and_zip = []
        for city in cities:
            city = city.strip()
            if city in body:
                indices = [i for i, x in enumerate(body) if x == city]
                for i in indices:
                    # because the body is separated by spaces, "New Delhi" would be in separate indices, so
                    # check if the index before it could add to the city name and still be valid
                    # EX: "Delhi" is valid and "New Delhi" is valid
                    check = body[i]
                    counter = 0
                    while check in cities:
                        if check in cities:
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
