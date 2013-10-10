from scrapy.spider import BaseSpider
from ..scrapers.link_scraper import LinkScraper
import os


class LinkScraperTest(BaseSpider):
    name = "link_scraper_test"
    start_urls = ["http://black.com/"]
    scraper = None

    def __init__(self, *args, **kwargs):
        super(LinkScraperTest, self).__init__(*args, **kwargs)
        self.scraper = LinkScraper()
        try:
            os.remove("../Output/link_scraper_output.txt")
        except OSError:
            pass

    def parse(self, response):
        links = self.scraper.parse(response)

        with open("../Output/link_scraper_output.txt", 'a') as f:
            for link in links:
                f.write(link + "\n")
                print(link)

        return links
