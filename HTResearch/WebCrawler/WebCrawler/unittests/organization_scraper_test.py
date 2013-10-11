from scrapy.spider import BaseSpider
from ..scrapers.link_scraper import LinkScraper
import os
import json
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
        orgs = self.scraper.parse(response)
        with open("../Output/organization_scraper_output.txt", 'a') as f:
            json_str = json.dumps(orgs)
            f.write(json.dumps(orgs))
            print(json_str)

        return orgs
