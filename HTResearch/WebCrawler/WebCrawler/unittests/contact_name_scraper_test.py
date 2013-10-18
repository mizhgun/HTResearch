from scrapy.spider import BaseSpider
#from scrapy import log
from ..scrapers.utility_scrapers import ContactNameScraper
import pdb


class ContactScraperTest(BaseSpider):
    name = "contact_name_scraper_test"
    #start_urls = ["http://www.prajwalaindia.com/contactus.html",
    #              "http://www.ijm.org/who-we-are/leadership",
    #              "http://www.tiss.edu/lefttop/faculty-staff/Administrators",
    #              "http://www.bba.org.in/?q=content/team"]
    start_urls = ["http://www.ijm.org/who-we-are/leadership"]

    def __init__(self, *args, **kwargs):
        super(ContactScraperTest, self).__init__(*args, **kwargs)
        self.scraper = ContactNameScraper()

    def parse(self, response):
        names = self.scraper.parse(response)
        for element in names:
            #print(element["name"])
            print(element)

        return names