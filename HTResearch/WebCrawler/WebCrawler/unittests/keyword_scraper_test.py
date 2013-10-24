from scrapy.spider import BaseSpider
from ..scrapers.utility_scrapers import KeywordScraper
import os


class KeywordScraperTest(BaseSpider):
    name = "keyword_scraper_test"
    start_urls = ["http://en.wikipedia.org/wiki/Nicolas_Cage"]
    scraper = None

    def __init__(self, *args, **kwargs):
        self.saved_path = os.getcwd()
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        super(KeywordScraperTest, self).__init__(*args, **kwargs)
        self.scraper = KeywordScraper()
        if not os.path.exists("../Output/"):
            os.makedirs("../Output")
        else:
            try:
                os.remove("../Output/keyword_scraper_output.txt")
            except OSError:
                pass

    def __del__(self):
        os.chdir(self.saved_path)

    def parse(self, response):
        keywords = self.scraper.parse(response)

        with open("../Output/keyword_scraper_output.txt", 'a') as f:
            for word in keywords:
                f.write(word + "\n")
                print(word)
        return keywords
