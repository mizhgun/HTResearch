from scrapy.spider import BaseSpider
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
        self.saved_path = os.getcwd()
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        super(AddressScraperTest, self).__init__(*args, **kwargs)
        self.scraper = OrgAddressScraper()
        if not os.path.exists("../Output/"):
            os.makedirs("../Output")
        else:
            try:
                os.remove("../Output/address_scraper_output.txt")
            except OSError:
                pass

    def __del__(self):
        os.chdir(self.saved_path)

    def parse(self, response):
        addresses = self.scraper.parse(response)

        with open("../Output/address_scraper_output.txt", 'a') as f:
            for element in addresses:
                f.write(element["city"] + " " + element["zip_code"] + "\n")
                print(element["city"] + " " + element["zip_code"])

        return addresses