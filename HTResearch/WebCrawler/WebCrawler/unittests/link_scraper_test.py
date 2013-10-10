from scrapy.spider import BaseSpider
from ..scrapers.link_scraper import LinkScraper

class LinkScraperTest(BaseSpider):
    name = "link_scraper_test"
    start_urls = ["http://black.com/"]
    scraper = None

    def __init__(self, *args, **kwargs):
        super(LinkScraperTest, self).__init__(*args, **kwargs)
        self.scraper = LinkScraper()

    def parse(self, response):
        links = self.scraper.parse(response)

        for element in links:
            print(element["url"])

        return links
        #TODO: unit tests should check a static input against an output
