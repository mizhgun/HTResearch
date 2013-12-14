from HTResearch.URLFrontier.urlfrontier import URLFrontierRules
from HTResearch.Utilities.context import URLFrontierContext
from HTResearch.Utilities.logutil import LoggingSection, get_logger
from HTResearch.Utilities.url_tools import UrlUtility

from springpython.context import ApplicationContext
from scrapers.document_scrapers import *
from scrapers.utility_scrapers import OrgUrlScraper
from scrapers.site_specific import StopTraffickingDotInScraper
from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy import log
import os

# Since this logger can be shared by the whole module, we can instantiate it here
logger = get_logger(LoggingSection.CRAWLER, __name__)


class OrgSpider(BaseSpider):
    name = 'org_spider'
    # empty start_urls, we're setting our own
    start_urls = []
    default_seed = "https://bombayteenchallenge.org/"
    # don't block on error codes
    handle_httpstatus_list = list(xrange(1, 999))

    def __init__(self, *args, **kwargs):
        super(OrgSpider, self).__init__(*args, **kwargs)

        # Define our Scrapers
        self.scrapers = []
        self.org_scraper = OrganizationScraper()
        self.meta_data_scraper = UrlMetadataScraper()
        self.scrapers.append(LinkScraper())
        self.url_frontier_rules = URLFrontierRules(blocked_domains=OrgSpider._get_blocked_domains())
        self.ctx = ApplicationContext(URLFrontierContext())
        self.url_frontier = self.ctx.get_object("URLFrontier")
        self.next_url_timeout = 10


    @staticmethod
    def _get_blocked_domains():
        blocked_domains = []
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Resources/blocked_org_domains.txt')) as f:
            for line in f:
                blocked_domains.append(line.rstrip())
        return blocked_domains

    def start_requests(self):
        """
        This method is called once by Scrapy to kick things off.
        We will get the first url to crawl from this.
        """

        logger.info('Starting requests to the Organization crawler')

        # first URL to begin crawling
        # Returns a URLMetadata model, so we have to pull the url field
        start_url_obj = self.url_frontier.next_url(self.url_frontier_rules)

        start_url = None
        if start_url_obj is None:
            start_url = OrgSpider.default_seed
        else:
            start_url = start_url_obj.url

        if __debug__:
            log.msg('START_REQUESTS : start_url = %s' % start_url)
            logger.debug('START_REQUESTS : start_url = %s' % start_url)

        request = Request(start_url, dont_filter=True)

        # Scrapy is expecting a list of Item/Requests, so use yield
        yield request

    def parse(self, response):
        ret = self.meta_data_scraper.parse(response)
        if ret is not None:
            yield ret
        ret = self.org_scraper.parse(response)
        if ret is not None:
            yield ret
            for scraper in self.scrapers:
                ret = scraper.parse(response)
                if isinstance(ret, type([])):
                    for item in ret:
                        yield item
                else:
                    yield ret

        next_url = self.url_frontier.next_url(self.url_frontier_rules)
        timeout = 0
        while next_url is None and timeout < self.next_url_timeout:
            timeout += 1
            next_url = self.url_frontier.next_url(self.url_frontier_rules)
        if next_url is not None:
            yield Request(next_url.url, dont_filter=True)
        else:
            self.url_frontier.empty_cache(self.url_frontier_rules)
            yield Request(self.default_seed, dont_filter=True)


class StopTraffickingSpider(BaseSpider):
    name = "stop_trafficking"
    allowed_domains = ['stoptrafficking.in']
    start_urls = ['http://www.stoptrafficking.in/Directory.aspx']

    def __init__(self, *args, **kwargs):
        self.saved_path = os.getcwd()
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        super(StopTraffickingSpider, self).__init__(*args, **kwargs)
        self.scraper = StopTraffickingDotInScraper()
        self.first = True
        self.directory_results = None

        if not os.path.exists("Output/"):
            os.makedirs("Output/")
        else:
            try:
                os.remove("Output/specific_page_scraper_output.txt")
            except OSError:
                pass

    def __del__(self):
        os.chdir(self.saved_path)

    def parse(self, response):
        """Parse this super specific page"""

        # if first time through...
        if self.first:
            self.first = False
            results = self.scraper.parse_directory(response)
            # grab directory entries
            self.directory_results = results
            #return Requests for each Popup page
            for result in results:
                yield Request(result.popup_url)

        # grab corresponding table entry 
        table_entry = next(entry for entry in self.directory_results if entry.popup_url == response.url)

        # cleanup
        if table_entry is not None:
            self.directory_results.remove(table_entry)

        items = self.scraper.parse_popup(response, table_entry)
        url_item = self._get_url_metadata(items)

        yield items
        yield url_item

    def _get_url_metadata(self, item):
        if not isinstance(item, ScrapedOrganization)\
                or item['organization_url'] is None or item['organization_url'] == "":
            return None

        url_item = ScrapedUrl()
        # Add http://'s since we removed them
        url_item['url'] = 'http://' + item['organization_url']
        url_item['domain'] = UrlUtility.get_domain(item['organization_url'])
        url_item['last_visited'] = datetime(1, 1, 1)

        return url_item