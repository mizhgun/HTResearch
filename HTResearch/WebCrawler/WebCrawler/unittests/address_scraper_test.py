from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import HtmlResponse
#from scrapy import log
from WebCrawler.scrapers.utility_scrapers import OrgUsAddressScraper
from WebCrawler.items import ScrapedAddress
import scrapy
import pdb

class EmailScraperTest(BaseSpider):
    name = "address_scraper_test"
    """start_urls = ["http://www.tiss.edu/TopMenuBar/contact-us/location-1",
                    "http://apneaap.org/contact/",
                    "http://www.aawc.in/contact_us.html",
                    "https://bombayteenchallenge.org/",
                    "http://www.compliance-matters.com/human-trafficking/",
                    "http://www.bba.org.in/?q=content/contact-us"] """
    start_urls = ["http://www.prajwalaindia.com/home.html"]

    def __init__(self, *args, **kwargs):
        super(EmailScraperTest, self).__init__(*args, **kwargs)
        self.scraper = OrgUsAddressScraper()

    def parse(self, response):
        addresses = self.scraper.parse(response)
        
        for element in addresses:
            print(element["address"])

        return addresses