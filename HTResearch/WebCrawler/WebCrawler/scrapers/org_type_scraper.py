from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
from WebCrawler.items import ScrapedPhoneNumber
import pdb
import re
import string

class OrgTypeScraper