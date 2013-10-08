from urlparse import urljoin

from scrapers.site_specific import StopTraffickingDotInScraper
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, TextResponse


class BasicCrawlSpider(BaseSpider):
    name = 'ht_research'
    allowed_domains = ['shaktivahini.org']
    start_urls = ['http://www.shaktivahini.org/']

    def parse(self, response):
        if isinstance(response, TextResponse):
            hxs = HtmlXPathSelector(response)
            links = hxs.select('//a')
            urls = []
            # Get unique urls from links
            for link in links:
                hrefs = link.select('@href').extract()
                for href in hrefs:
                    url = urljoin(response.url, href)
                    if url not in urls:
                        urls.append(url)

            return [ Request(url) for url in urls ]


class StopTraffickingSpider(BaseSpider):
    name = "stop_trafficking"
    allowed_domains = ['stoptrafficking.in']
    start_urls = ['http://www.stoptrafficking.in/Directory.aspx']

    def __init__(self, *args, **kwargs):
        super(StopTraffickingSpider, self).__init__(*args, **kwargs)
        self.scraper = StopTraffickingDotInScraper()
        self.first = True
        self.directory_results = None

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
        table_entry =  next(entry for entry in self.directory_results if entry.popup_url == response.url)

        # cleanup
        if table_entry is not None:
            self.directory_results.remove(table_entry)

        items = self.scraper.parse_popup(response, table_entry)

        return items