from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy import log
from WebCrawler.scrapers.email_scraper import EmailScraper
import scrapy
import pdb
import os

class EmailScraperTest(BaseSpider):
    name = "email_scraper_test"
    start_urls = ["http://us.blizzard.com/en-us/company/about/contact.html", "https://bombayteenchallenge.org/"]

    def __init__(self, *args, **kwargs):
        super(EmailScraperTest, self).__init__(*args, **kwargs)
        self.scraper = EmailScraper()

    def parse(self, response):
        emails = self.scraper.parse(response)

        print emails