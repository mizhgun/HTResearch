from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import HtmlResponse
#from scrapy import log
from WebCrawler.scrapers.email_scraper import EmailScraper
from WebCrawler.items import ScrapedEmail
import scrapy
import pdb

class EmailScraperTest(BaseSpider):
    name = "email_scraper_test"
    start_urls = ["http://us.blizzard.com/en-us/company/about/contact.html", "https://bombayteenchallenge.org/"]

    def __init__(self, *args, **kwargs):
        super(EmailScraperTest, self).__init__(*args, **kwargs)
        self.scraper = EmailScraper()

    def parse(self, response):
        emails = self.scraper.parse(response)
        
        for element in emails:
            print(element["email"])

        return emails