from scrapy.spider import BaseSpider
from WebCrawler.scrapers.utility_scrapers import OrgTypeScraper

class OrgTypeScraperTest(BaseSpider):
    name = "org_type_scraper_test"
    #start_urls = ["http://nhrc.nic.in/ContactUs.htm",
    #              "https://bombayteenchallenge.org/"]
    start_urls = [
        'https://bombayteenchallenge.org/',
        'http://www.nsa.gov/',
        'http://www.halftheskymovement.org/',
    ]

    def __init__(self, *args, **kwargs):
        super(OrgTypeScraperTest, self).__init__(*args, **kwargs)
        self.scraper = OrgTypeScraper()
        self.on = True

    def parse(self, response):
        types = self.scraper.parse(response)

        for type in types:
            print(type)

        return types