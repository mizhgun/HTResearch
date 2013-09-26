from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy import log
from WebCrawler.scrapers.email_scraper import EmailScraper
import scrapy
import pdb
import os
import unittest

class EmailScraperTest(BaseSpider):
    name = "email_scraper_test"
    start_urls = ["http://us.blizzard.com/en-us/company/about/contact.html", "https://bombayteenchallenge.org/"]

    def __init__(self, *args, **kwargs):
        super(EmailScraperTest, self).__init__(*args, **kwargs)
        self.scraper = EmailScraper()

    def parse(self, response):
        emails = self.scraper.parse(response)

        return emails

class EmailTest(unittest.TestCase):
    def test_email_scraper(self):
        bliz_emails = ["sitelicense@blizzard.com","tours@blizzard.com"]
        btc_emails = ["tvarghese@bombayteenchallenge.org","kkdevearaj@bombayteenchallenge.org"]
        test = EmailScraperTest()
        print test.parse()


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0]:
            raise