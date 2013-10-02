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
    
    def __init__(self):
        phone_nums = []
        
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        us_format_regex = re.compile(r'\b(?! )1?\s?[(-./]?\s?[2-9][0-8][0-9]\s?[)-./]?\s?[2-9][0-9]{2}\s?\W?\s?[0-9]{4}\b')
        india_format_regex = re.compile(r'\b(?!\s)(?:91[-./\s]+)?[0-9]+[0-9]+[-./\s]?[0-9]?[0-9]?[-./\s]?[0-9]?[-./\s]?[0-9]{5}[0-9]?\b')
        # body will get phone numbers that are just text in the body
        body = hxs.select('//body').re(us_format_regex)
        body2 = hxs.select('//body').re(india_format_regex)

        phone_nums = body
        #phone_nums = list(set(body) | set(body2))     

        # Remove unicode indicators
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
