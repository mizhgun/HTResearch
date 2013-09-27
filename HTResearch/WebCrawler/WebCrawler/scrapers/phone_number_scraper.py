from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
from WebCrawler.items import ScrapedPhoneNumber
import pdb
import re
import string

class PhoneNumberScraper(BaseSpider):
    name = "phone_number_scraper_test"
    start_urls = ["http://www.yellowpages.com/lincoln-ne/restaurants"]
    allowed_domains = ["unl.edu"]
    
    def __init__(self):
        phone_nums = []
        
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        regex = re.compile(r'\s(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?')
        #regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}\b')
        # body will get phone numbers that are just text in the body
        body = hxs.select('//body').re(regex)
        
        footer = hxs.select('//footer').re(regex)

        # hrefs will get phone numbers from hrefs
        hrefs = hxs.select("//./a/@href").re(regex)
        
        intersection = list(set(body) & set(hrefs))  
        phone_nums = body     

        for num in intersection:
            phone_nums.remove(num)

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

        pdb.set_trace()
        return phone_nums_list
