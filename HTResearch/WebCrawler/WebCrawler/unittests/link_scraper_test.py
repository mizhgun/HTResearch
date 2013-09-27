from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy import log
from WebCrawler.scrapers.link_scraper import LinkScraper
import scrapy
import pdb
import os

class LinkScraperTest(BaseSpider):
    name = "link_scraper_test"
    start_urls = ["http://en.wikipedia.org/wiki/Web_scraping"]
    scraper = None

    def __init__(self, *args, **kwargs):
        super(LinkScraperTest, self).__init__(*args, **kwargs)
        self.scraper = LinkScraper()

    def parse(self, response):
        links = self.scraper.parse(response)

        print links
