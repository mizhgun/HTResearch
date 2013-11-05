from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from ..items import ScrapedUrl


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
        links = self._link_extractor.extract_links(response)

        # add these links to our Url item
        urls = list()
        for link in links:
            url = ScrapedUrl()
            url['url'] = link.url
            if url not in urls:
                urls.append(url)

        return urls