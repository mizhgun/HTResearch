from scrapy.spider import BaseSpider
from ..scrapers.utility_scrapers import OrgTypeScraper
import os

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
        if not os.path.exists("../Output/"):
            os.makedirs("../Output")
        else:
            try:
                os.remove("../Output/org_type_scraper_output.txt")
            except OSError:
                pass

    def parse(self, response):
        types = self.scraper.parse(response)

        with open('../Output/org_type_scraper_output.txt', 'a') as f:
            for type in types:
                f.write(type + '\n')
                print(type)

        return types