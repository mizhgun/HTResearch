from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
import pdb

class HtResearchSpider(BaseSpider):
    name = ""
    allowed_domains = ["domain"]
    start_urls = [
                  "full links"
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        # Data to find using XPath