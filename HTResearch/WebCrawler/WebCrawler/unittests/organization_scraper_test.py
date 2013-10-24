from scrapy.spider import BaseSpider
import os
from ..scrapers.document_scrapers import OrganizationScraper


class OrganizationScraperTest(BaseSpider):
    name = 'organization_scraper_test'
    start_urls = [
        'https://bombayteenchallenge.org/',
    ]
    scraper = None

    def __init__(self, *args, **kwargs):
        super(OrganizationScraperTest, self).__init__(*args, **kwargs)
        self.scraper = OrganizationScraper()
        if not os.path.exists("../Output/"):
            os.makedirs("../Output")
        else:
            try:
                os.remove("../Output/organization_scraper_output.txt")
            except OSError:
                pass

    def parse(self, response):
        org = self.scraper.parse(response)
        with open("../Output/organization_scraper_output.txt", 'a') as f:
            string = str(org)
            f.write(string)
            print(string)

        return org
