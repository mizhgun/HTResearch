from urlparse import urljoin

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, TextResponse
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.item import Item, Field

class BasicCrawlSpider(BaseSpider):
    name = 'basic_crawl'
    allowed_domains = [ 'www.stoptrafficking.net' ]
    start_urls = [ 'http://www.stoptrafficking.net/' ]

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