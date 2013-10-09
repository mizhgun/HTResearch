import unittest
from scrapy.selector import HtmlXPathSelector
from scrapy.http import HtmlResponse
from scrapy import log
import scrapy
import pdb
import os
from ..items import ScrapedOrganization
import subprocess
import json

class ScraperTests(unittest.TestCase):
    def test_email_scraper(self):
        # Runs the test spider and pipes the printed output to "output"
        p = subprocess.Popen('scrapy crawl email_scraper_test', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = p.communicate()

        # Splits the results based on automatically added characters
        emails = output.splitlines()
        emails = emails[:len(emails)-1]

        # Hardcoded results based on the sites that were crawled
        assert_list = ["sgnhrc@nic.in",
                       "covdnhrc@nic.in",
                       "anilpradhanshilong@gmail.com",
                       "snarayan1946@gmail.com",
                       "kkdevaraj@bombayteenchallenge.org",
                       "tvarghese@bombayteenchallenge.org"]

        for test in assert_list:
            self.assertIn(test, emails, "Email " + test + "not found")

    def test_link_scraper(self):
        p = subprocess.Popen('scrapy crawl link_scraper_test', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = p.communicate()
        urls = output.splitlines()
        urls = [x.lower() for x in urls]

        assert_list = ["http://www.black.com/"
                       ]

        for test in assert_list:
            self.assertIn(test.lower(), urls, "URL " + test + " was not found")

    def test_organization_scraper(self):
        p = subprocess.Popen('scrapy crawl organization_scraper_test', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = p.communicate()
        """assert_value = {
            'name': 'Bombay Teen Challenge',
            'address': '7742 Spalding Drive',
            'types': [ 'religious' ],
            'phone_number': '+1 615.712.4863',
            'email': 'tvarghese@bombayteenchallenge.org',
            'contacts': [],
            'organization_url': 'https://bombayteenchallenge.org/',
            'partners': [],
        }"""
        organization = json.loads(output)

        # TODO: Assert equality

if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0]:
            raise