from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import HtmlResponse
from WebCrawler.scrapers.utility_scrapers import KeywordScraper
import scrapy

class KeywordScraperTest(BaseSpider):
    name = "keyword_scraper_test"
    start_urls = ["http://en.wikipedia.org/wiki/Nicolas_Cage"]

    def __init__(self, *args, **kwargs):
        super(KeywordScraperTest, self).__init__(*args, **kwargs)
        self.scraper = KeywordScraper()

    def parse(self, response):
        keywords = self.scraper.parse(response)
        return keywords
