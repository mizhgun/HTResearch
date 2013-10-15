from urlparse import urljoin
from HTResearch.WebCrawler.WebCrawler.scrapers.link_scraper import LinkScraper

from scrapers.site_specific import StopTraffickingDotInScraper
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, TextResponse
from scrapy import log
import os
import pdb


class BasicCrawlSpider(BaseSpider):
    name = 'ht_research'
    # empty list means all domains allowed
    allowed_domains = []
    start_urls = []
    link_scraper = LinkScraper()

    def start_requests(self):
        """
        This method is called once by Scrapy to kick things off.
        We will get the first url to crawl from this.
        """

        # first URL to begin crawling
        # TODO: use the actual URL Frontier, for now use test data
        # start_url = url_frontier.next_url()
        start_url = 'http://www.shaktivahini.org/'

        if __debug__:
            log.msg('START_REQUESTS : start_url = %s' % start_url)

        request = Request(start_url, dont_filter=True)

        # Scrapy is expecting a list of Item/Requests, so use yield
        yield request

    def parse(self, response):
        if isinstance(response, TextResponse):
            links = self.link_scraper.parse(response)
            # Note: These links are ScrapedURL Items, NOT Requests
            for link in links:
                yield link

        # TODO: Yield the next url from URL Frontier
        # yield Request(url_frontier.next_url())
        for link in links:
            yield Request(link['url'], dont_filter=True)


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
