import unittest
from scrapy.selector import HtmlXPathSelector
from scrapy.http import HtmlResponse
from scrapy import log
import scrapy
import pdb
import os
import subprocess

class ScraperTests(unittest.TestCase):
    def test_email_scraper(self):
        # Runs the test spider and pipes the printed output to "output"
        p = subprocess.Popen('scrapy crawl email_scraper_test', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = p.communicate()

        # Splits the results based on automatically added characters
        emails = output.split("\r\n")
        emails = emails[:len(emails)-1]

        # Hardcoded results based on the sites that were crawled
        assert_list = ["sitelicense@blizzard.com",
                       "tours@blizzard.com",
                       "kkdevaraj@bombayteenchallenge.org",
                       "tvarghese@bombayteenchallenge.org"]
        for test in assert_list:
            self.assertIn(test, emails, "Email not found")

    def test_link_scraper(self):
        p = subprocess.Popen('scrapy crawl link_scraper_test', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = p.communicate()
        urls = output.split("\r\n")
        urls = urls[:len(urls)-1]
        urls = [x.lower() for x in urls]

        assert_list = ["http://www.black.com/"
                       ]

        for test in assert_list:
            self.assertIn(test.lower(), urls, "URL " + test + " was not found")

if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0]:
            raise