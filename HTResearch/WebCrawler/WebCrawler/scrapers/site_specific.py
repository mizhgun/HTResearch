import re
from scrapy import log
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, TextResponse, HtmlResponse
from WebCrawler.items import ScrapedOrganization

class StopTraffickingDotInScraper:
    """An ad hoc scraper for the page: http://www.stoptrafficking.in/Directory.aspx"""

    # parses the onclick attribute for the cid we will use to find the popup windows
    # use first .group(1) to get the cid out
    onclick_re = re.compile(r'^javascript:window\.open\(\'ServicesPopup\.aspx\?cid=(\d+)\',.*$')

    class _TableData:
        """An intermediate class to hold table data"""

        def __init__(self, state = None, district = None,
                     org_name = None, popup_url = None, categories = None,
                     contacts = None, contact_numbers = None):
            self.state = state
            self.district = district
            self.org_name = org_name
            self.popup_url = popup_url
            self.categories = categories
            self.contacts = contacts
            self.contact_numbers = contact_numbers

        def __str__(self):
            ret = "<" + self.state + ", "
            ret += self.district + ", "
            ret += self.org_name + ", "
            ret += self.popup_url + ", "
            ret += self.categories + ", "
            ret += self.contacts + ", "
            ret += self.contact_numbers + ">"
            return ret

    def __init__(self):
        pass

    def parse_directory(self, response):
        """Scrape the HttpRequest.Response for Organizations"""

        # Reference regex so I only have to type this once
        regex = StopTraffickingDotInScraper.onclick_re

        # Create XPath selector
        if isinstance(response, TextResponse):
            hxs = HtmlXPathSelector(response)
        
            # get our data from the gvFaq table
            table = hxs.select('//table[@id="gvFaq"]')
            # first row is headers, so grab everything after
            rows = table.select('tr[position() > 1]')

            # collect values from each column
            states = rows.select('td[1]/font/text()').extract()
            districts = rows.select('td[2]/font/text()').extract()
            orgnames = rows.select('td[3]/font/a/text()').extract()
            onclicks = rows.select('td[3]/font/a/@onclick').extract()
            categories = rows.select('td[4]/font/text()').extract()
            contacts = rows.select('td[5]/font/text()').extract()
            contact_numbers = rows.select('td[6]/font/text()').extract()

            #extract cids from onclicks
            cids = []
            for onclick in onclicks:
                cids.append(regex.match(onclick).group(1))

            items = self._create_items(states, districts, orgnames, categories, contacts, contact_numbers, cids)

        return items 

    def _create_items(self, states, districts, orgnames, categories, contacts, contact_numbers, cids):
        # grab count from states, but should be same for all
        count = len(states)
        urls = [self._map_cid_to_url(cid) for cid in cids]
        
        items = []
        # iterate over states, but we could use anything
        for i in xrange(0, count):
            item = self._TableData(states[i], districts[i],
                                   orgnames[i], urls[i],
                                   categories[i], contacts[i],
                                   contact_numbers[i])
            items.append(item)

        return items

    def _map_cid_to_url(self, cid):
        return "http://www.stoptrafficking.in/ServicesPopup.aspx?cid=" + cid