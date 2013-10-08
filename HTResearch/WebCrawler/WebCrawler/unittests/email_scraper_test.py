from scrapy.spider import BaseSpider
from ..scrapers.utility_scrapers import EmailScraper
import pdb

class EmailScraperTest(BaseSpider):
    name = "email_scraper_test"
    start_urls = ["http://nhrc.nic.in/ContactUs.htm",
                  "http://bombayteenchallenge.org/",
                  "http://www.tiss.edu/TopMenuBar/contact-us/location-1",
                  "http://apneaap.org/contact/",
                  "http://www.aawc.in/contact_us.html"
                  ]

    def __init__(self, *args, **kwargs):
        super(EmailScraperTest, self).__init__(*args, **kwargs)
        self.scraper = EmailScraper()

    def parse(self, response):
        emails = self.scraper.parse(response)
        
        for element in emails:
            print(element["email"])

        return emails
