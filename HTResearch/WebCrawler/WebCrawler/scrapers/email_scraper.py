from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
from WebCrawler.items import Email
import pdb
import re

class EmailScraper(BaseSpider):

    def __init__(self):
        emails = []

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        
        # body will get emails that are just text in the body
        body = hxs.select('//body').re(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}\b')
        
        # hrefs will get emails from hrefs
        hrefs = hxs.select("//./a[contains(@href,'@')]/@href").re(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}\b')
        
        emails = body+hrefs

        # Take out the unicode or whatever
        for i in range(len(emails)):
            emails[i] = emails[i].encode('ascii','ignore')

        # Makes it a set then back to a list to take out duplicates that may have been both in the body and links
        emails = list(set(emails))
        return emails