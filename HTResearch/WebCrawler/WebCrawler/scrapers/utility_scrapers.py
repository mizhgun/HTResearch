from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
from WebCrawler.items import *
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


class NameScraper:

    def __init__(self):
        self.names = []

class OrgUsAddressScraper:
    def parse(self, response):
        # maybe use google maps api to check if real address?

        hxs = HtmlXPathSelector(response)

        ## if super duper pathetically desperate, use if response.url == url and then just call the needed code

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

        address_list = []
        for address in addresses:
            item = ScrapedAddress()
            item['address'] = address
            address_list.append(item)
        pdb.set_trace()
        return address_list

#class OrgIndiaAddressScraper:
#    def parse(self, response):
#        return "POOP"

class OrgContactsScraper:

    def __init__(self):
        self.contacts = []

class OrgPartnersScraper:

    def __init__(self):
        self.partners = []

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
