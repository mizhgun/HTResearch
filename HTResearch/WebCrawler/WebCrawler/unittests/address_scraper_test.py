from scrapy.spider import BaseSpider
#from scrapy import log
from ..scrapers.utility_scrapers import OrgAddressScraper
import os
import pdb


class AddressScraperTest(BaseSpider):
    name = "address_scraper_test"
    start_urls = ["http://www.tiss.edu/TopMenuBar/contact-us/location-1",
                  "http://apneaap.org/contact/",
                  "http://www.aawc.in/contact_us.html",
                  "https://bombayteenchallenge.org/",
                  "http://www.compliance-matters.com/human-trafficking/",
                  "http://www.bba.org.in/?q=content/contact-us",
                  "http://www.prajwalaindia.com/home.html"]
    #start_urls = ["http://www.aawc.in/contact_us.html"]

    def __init__(self, *args, **kwargs):
        super(AddressScraperTest, self).__init__(*args, **kwargs)
        self.scraper = OrgAddressScraper()
        try:
            os.remove("../Output/address_scraper_output.txt")
        except OSError:
            pass

    def parse(self, response):
        addresses = self.scraper.parse(response)

        with open("../Output/address_scraper_output.txt", 'a') as f:
            for element in addresses:
                f.write(element["city"] + " " + element["zip_code"] + "\n")
                print(element["city"] + " " + element["zip_code"])

        return addresses