import unittest
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import HtmlResponse
from scrapy import log
import scrapy
import pdb
import os
import subprocess

class ScraperTests(unittest.TestCase):
    def test_email_scraper(self):
        p = subprocess.Popen('scrapy crawl email_scraper_test', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = p.communicate()
        emails = output.split("\r\n")
        emails = emails[:len(emails)-1]
        pdb.set_trace()

    def test_link_scraper(self):
        p = subprocess.Popen('scrapy crawl link_scraper_test', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = p.communicate()
        urls = output.split("\r\n")
        urls = urls[:len(urls)-1]
        pdb.set_trace()

if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0]:
            raise