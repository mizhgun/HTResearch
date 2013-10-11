from scrapy.spider import BaseSpider
from ..scrapers.utility_scrapers import EmailScraper
import os
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
        self.saved_path = os.getcwd()
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        super(EmailScraperTest, self).__init__(*args, **kwargs)
        self.scraper = EmailScraper()
        if not os.path.exists("../Output/"):
            os.makedirs("../Output")
        else:
            try:
                os.remove("../Output/email_scraper_output.txt")
            except OSError:
                pass

    def __del__(self):
        os.chdir(self.savedPath)

    def parse(self, response):
        emails = self.scraper.parse(response)
        with open("../Output/email_scraper_output.txt", 'a') as f:
            for element in emails:
                f.write(element["email"] + "\n")
                print(element["email"])

        return emails
