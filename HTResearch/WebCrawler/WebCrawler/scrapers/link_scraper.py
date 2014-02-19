from sgmllib import SGMLParseError
from datetime import datetime

from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

from ..items import ScrapedUrl

from HTResearch.DataModel.model import PageRankInfo, PageRankVector, UrlCountPair
from HTResearch.Utilities.url_tools import UrlUtility
from HTResearch.Utilities.logutil import get_logger, LoggingSection


_linkscraper_logger = get_logger(LoggingSection.CRAWLER, __name__)


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
        except SGMLParseError as e:
            # Page was poorly formatted, oh well
            _linkscraper_logger.error('Exception encountered when link extracting page')
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


class PageRankScraper:
    """A scraper to generate Page Rank Information for a page"""

    def __init__(self):
        self._link_extractor = SgmlLinkExtractor()

    def parse(self, response):
        """Scrape a spider's HttpRequest.Response for links"""

        # get domain
        try:
            org_domain = UrlUtility.get_domain(response.request.url, False)
        except Exception as e:
            _linkscraper_logger.error('Exception encountered when trying to find the domain of ' + response.request.url)

        # sanity check
        if self._link_extractor is None:
            self._link_extractor = SgmlLinkExtractor()

        # use scrapy SgmlLinkExtractor to extract links
        try:
            links = self._link_extractor.extract_links(response)
        except SGMLParseError as e:
            # Page was poorly formatted, oh well
            _linkscraper_logger.error('Exception encountered when PageRankInfo scraping page')
            return None

        # add these links to our Page Rank Info
        page_rank_info = {
            "total": 0,
            "total_with_self": 0,
            "references": []
        }
        for link in links:
            url = link.url
            try:
                domain = UrlUtility.get_domain(url, False)
            except Exception as e:
                _linkscraper_logger.error('Exception encountered when trying to find the domain of ' + url)
                continue
            ref_found = False
            for ref in page_rank_info["references"]:
                if ref["org_domain"] == domain:
                    ref_found = True
                    ref["count"] += 1
                    ref["pages"][0]["count"] += 1
                    page_rank_info["total_with_self"] += 1
                    if domain != org_domain:
                        page_rank_info["total"] += 1
                    break;
            if not ref_found:
                page_rank_info["references"].append(
                    {
                        "org_domain": domain,
                        "count": 1,
                        "pages": [
                            {
                                "url": response.url,
                                "count": 1
                            }
                        ]
                    }
                )
                page_rank_info["total_with_self"] += 1
                if domain != org_domain:
                    page_rank_info["total"] += 1

        return page_rank_info
