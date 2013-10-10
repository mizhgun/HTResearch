from scrapy.spider import BaseSpider
from ..scrapers.utility_scrapers import KeywordScraper
import scrapy

class KeywordScraperTest(BaseSpider):
    name = "keyword_scraper_test"
    start_urls = ["http://en.wikipedia.org/wiki/Nicolas_Cage"]
    scraper = None

    def __init__(self, *args, **kwargs):
        super(KeywordScraperTest, self).__init__(*args, **kwargs)
        self.scraper = KeywordScraper()

    def parse(self, response):
        keywords = self.scraper.parse(response)
        for word in keywords:
            print word
        return keywords
