from scrapy.spider import BaseSpider
from ..scrapers.utility_scrapers import ContactNameScraper
import pdb


class EmailScraperTest(BaseSpider):
    name = "contact_name_scraper_test"
    start_urls = ["http://www.prajwalaindia.com/contactus.html"
                  ]

    def __init__(self, *args, **kwargs):
        super(EmailScraperTest, self).__init__(*args, **kwargs)
        self.scraper = ContactNameScraper()

    def parse(self, response):
        contacts = self.scraper.parse(response)

        for element in contacts:
            print(element["name"])

        return contacts
