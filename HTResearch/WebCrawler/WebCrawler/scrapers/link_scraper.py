from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy import log

class LinkScraper:
    """A scraper to find all URLs in a page """
    _link_extractor = None

    def __init__(self):
        _link_extractor = SgmlLinkExtractor()

    def parse(self, response):
        """Scrape a spider's HttpRequest.Response for links"""
        
        # sanity check
        if self._link_extractor is None:
            self._link_extractor = SgmlLinkExtractor()
        
        # use scrapy SgmlLinkExtractor to extract links
        links = self._link_extractor.extract_links(response)