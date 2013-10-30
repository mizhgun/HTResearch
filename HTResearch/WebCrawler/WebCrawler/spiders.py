from HTResearch.URLFrontier.urlfrontier import URLFrontier
from HTResearch.WebCrawler.WebCrawler.scrapers.link_scraper import LinkScraper

from scrapers.document_scrapers import *
from scrapers.site_specific import StopTraffickingDotInScraper
from scrapy.spider import BaseSpider
from scrapy.http import Request, TextResponse
from scrapy import log
import os


class OrgSpider(BaseSpider):
    name = 'org_spider'
    # empty start_urls, we're setting our own
    start_urls = []

    def __init__(self, *args, **kwargs):
        super(OrgSpider, self).__init__(*args, **kwargs)

        # Define our Scrapers
        self.scrapers = []
        self.scrapers.append(OrganizationScraper())
        self.scrapers.append(LinkScraper())
        self.scrapers.append(UrlMetadataScraper())

        self.url_frontier = URLFrontier()

    def start_requests(self):
        """
        This method is called once by Scrapy to kick things off.
        We will get the first url to crawl from this.
        """

        # first URL to begin crawling
        # Returns a URLMetadata model, so we have to pull the url field
        start_url = self.url_frontier.next_url().url

        print start_url
        if __debug__:
            log.msg('START_REQUESTS : start_url = %s' % start_url)

        request = Request(start_url, dont_filter=True)

        # Scrapy is expecting a list of Item/Requests, so use yield
        yield request

    def parse(self, response):
        for scraper in self.scrapers:
            ret = scraper.parse(response)
            if isinstance(ret, type([])):
                for item in ret:
                    yield item
            else:
                yield ret

        print response.url
        yield Request(self.url_frontier.next_url().url, dont_filter=True)


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
            return [Request(result.popup_url) for result in results]

        # grab corresponding table entry 
        table_entry = next(entry for entry in self.directory_results if entry.popup_url == response.url)

        # cleanup
        if table_entry is not None:
            self.directory_results.remove(table_entry)

        items = self.scraper.parse_popup(response, table_entry)

        with open("Output/specific_page_scraper_output.txt", 'a') as f:
            f.write(str(items) + "\n\n")

        return items
