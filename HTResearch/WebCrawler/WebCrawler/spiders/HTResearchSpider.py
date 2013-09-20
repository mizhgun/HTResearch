from scrapy.spider import CrawlSpider
from scrapy.selector import HtmlXPathSelector
import pdb

class HtResearchSpider(CrawlSpider):
    name = 'ht_research'
    #allowed_domains = ['domain']
    start_urls = [
        'https://bombayteenchallenge.org/',
        'http://www.catholicrelief.org/slavery-human-trafficking/',
        'http://www.compliance-matters.com/human-trafficking/',
        'http://sharedhope.wordpress.com/2010/08/23/anti-trafficking-report-india/',
        'http://www.oasisindia.org/index.php/our-work/anti-human-trafficking',
        'http://apneaap.org/',
        'http://www.aawc.in/'
    ]

    rules = (
        Rule(SgmlLinkExtractor(callback='parse_item')),
    )

    def parse_item(self, response):
        self.log('found item page: %s' % response.url)

        hxs = HtmlXPathSelector(response)
        
        # TODO: Scrape the data using a scraper that Paul is supposedly going to create
        # e.g. scraper.scrape(hxs) ???

        return None

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        # Data to find using XPath