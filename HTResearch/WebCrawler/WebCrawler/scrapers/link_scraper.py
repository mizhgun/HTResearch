from sgmllib import SGMLParseError
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from ..items import ScrapedUrl
from HTResearch.Utilities.url_tools import UrlUtility
from datetime import datetime


class LinkScraper:
    """A scraper to find all URLs in a page """

    def __init__(self):
        self._link_extractor = SgmlLinkExtractor()

    def parse(self, response):
        """Scrape a spider's HttpRequest.Response for links"""

        # sanity check
        if self._link_extractor is None:
            self._link_extractor = SgmlLinkExtractor()
        
        # use scrapy SgmlLinkExtractor to extract links
        try:
            links = self._link_extractor.extract_links(response)
        except SGMLParseError:
            # Page was poorly formatted, oh well
            return []

        # add these links to our Url item
        urls = list()
        for link in links:
            url = ScrapedUrl()
            url['url'] = link.url
            url['domain'] = UrlUtility.get_domain(link.url)
            url['last_visited'] = datetime(1, 1, 1)
            if url not in urls:
                urls.append(url)

        return urls