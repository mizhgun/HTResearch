from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import TextResponse
#from scrapy import log
from WebCrawler.scrapers.utility_scrapers import EmailScraper, OrgTypeScraper
from WebCrawler.items import ScrapedEmail
import scrapy
import pdb

class OrgTypeScraperTest(BaseSpider):
    name = "org_type_scraper_test"
    #start_urls = ["http://nhrc.nic.in/ContactUs.htm",
    #              "https://bombayteenchallenge.org/"]
    start_urls = [
        'http://www.aawc.in/',
        'http://apneaap.org/',
        'http://www.oasisindia.org',
        'https://bombayteenchallenge.org/',
        'http://www.compliance-matters.com/human-trafficking/',
        'http://www.rescuefoundation.net/',
        'http://www.unicef.org/india/',
        'http://www.freedom.firm.in/',
        'http://www.ijm.org/',
        'http://www.stop-india.org',
        'http://www.sanlaapindia.org/',
        'http://www.prajwalaindia.com',
        'http://www.bba.org.in/',
        'http://www.preranaantitrafficking.org/',
        'http://www.stoptrafficking.in/',
        'http://www.lawyerscollective.org/',
        'http://www.halftheskymovement.org/',
        'http://www.equalitynow.org/',
        'http://www.catwinternational.org/',
        'http://www.centsofrelief.org/',
    ]

    def __init__(self, *args, **kwargs):
        super(OrgTypeScraperTest, self).__init__(*args, **kwargs)
        self.scraper = OrgTypeScraper()
        self.on = True

    def parse(self, response):
        types = self.scraper.parse(response)
        
        if self.on:
            print('')
            print('----------------')
            print(response.url)
            # DEBUG: stop at bombayteenchallenge.org
            if 'bombayteenchallenge' in response.url:
                self.on = False
            for i in range(len(types)):
                print('Type #%d: %s' % (i + 1, types[i]))

        return types