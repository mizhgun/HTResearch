from urlparse import urljoin

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, TextResponse

class BasicCrawlSpider(BaseSpider):
    name = 'basic_crawl'
    allowed_domains = [ 'shaktivahini.org' ]
    start_urls = [ 'http://www.shaktivahini.org/' ]

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