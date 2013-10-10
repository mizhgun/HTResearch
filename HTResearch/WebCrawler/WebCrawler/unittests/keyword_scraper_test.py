from scrapy.spider import BaseSpider
from ..scrapers.utility_scrapers import KeywordScraper
import os
import scrapy

class KeywordScraperTest(BaseSpider):
    name = "keyword_scraper_test"
    start_urls = ["http://en.wikipedia.org/wiki/Nicolas_Cage"]
    scraper = None

    def __init__(self, *args, **kwargs):
        super(KeywordScraperTest, self).__init__(*args, **kwargs)
        self.scraper = KeywordScraper()
        if not os.path.exists("../Output/"):
            os.makedirs("../Output")
        else:
            try:
                os.remove("../Output/keyword_scraper_output.txt")
            except OSError:
                pass

    def parse(self, response):
        keywords = self.scraper.parse(response)

        with open("../Output/keyword_scraper_output.txt", 'a') as f:
            for word in keywords:
                f.write(word + "\n")
                print(word)
        return keywords
