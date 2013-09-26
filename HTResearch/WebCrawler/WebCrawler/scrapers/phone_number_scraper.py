from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
from WebCrawler.items import S
import pdb
import re
import string

class PhoneNumberScraper(BaseSpider):

    def __init__(self):
        phone_nums = []

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        
        # body will get emails that are just text in the body
        body = hxs.select('//body').re(r'^(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?$')
        
        # hrefs will get emails from hrefs
        #hrefs = hxs.select("//./a[contains(@href,'@')]/@href").re(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}\b')
        
        phone_nums = body#+hrefs

        # Take out the unicode or whatever
        for i in range(len(phone_nums)):
            phone_nums[i] = phone_nums[i].encode('ascii','ignore')

        # Makes it a set then back to a list to take out duplicates that may have been both in the body and links
        phone_nums = list(set(phone_nums))

        # Make the list an item
        phone_nums_list = []
        for num in phone_nums:
            item = ScrapedPhoneNumber()
            item['phone_number'] = num
            phone_nums_list.append(item)

        return phone_nums_list