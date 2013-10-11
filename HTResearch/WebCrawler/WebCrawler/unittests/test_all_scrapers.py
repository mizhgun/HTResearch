import unittest
import pdb
import subprocess
import os


class ScraperTests(unittest.TestCase):
    def test_address_scraper(self):
        # Runs the test spider and pipes the printed output to "output"
        p = subprocess.Popen('scrapy crawl address_scraper_test', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = p.communicate()

        # Splits the results based on automatically added characters
        addresses = output.splitlines()

        # Hardcoded results based on the sites that were crawled
        assert_list = ["Guwahati 781001",
                       "Tuljapur 413601",
                       "Hyderabad 500030",
                       "Mumbai 400088",
                       "New Delhi 110003",
                       "Hyderabad 500002",
                       "Mumbai 400064",
                       "New Delhi 110019",
                       "Mumbai 400052"]

        for test in assert_list:
            self.assertIn(test, addresses, test + " not found")

    def test_email_scraper(self):
        # Runs the Test spider and pipes the printed output to "output"
        os.chdir(os.path.join(os.pardir, os.pardir))
        p = subprocess.Popen('scrapy crawl email_scraper_test', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = p.communicate()

        # Splits the results based on automatically added characters
        emails = output.splitlines()

        # Hardcoded results based on the sites that were crawled
        assert_list = ["sgnhrc@nic.in",
                       "covdnhrc@nic.in",
                       "anilpradhanshilong@gmail.com",
                       "snarayan1946@gmail.com",
                       "tvarghese@bombayteenchallenge.org"]

        for test in assert_list:
            self.assertIn(test, emails, "Email " + test + " not found")

    def test_link_scraper(self):
        p = subprocess.Popen('scrapy crawl link_scraper_test', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = p.communicate()
        urls = output.splitlines()
        urls = [x.lower() for x in urls]

        assert_list = [
            'http://www.stoptrafficking.net/about',
            'http://www.stoptrafficking.net/services/training',
            'http://visit.unl.edu/',
            'http://www.unl.edu/ucomm/prospective/',
        ]

        for test in assert_list:
            self.assertIn(test.lower(), urls, "URL " + test + " was not found")

    def test_keyword_scraper(self):
        # Runs the Test spider and pipes the printed output to "output"
        p = subprocess.Popen('scrapy crawl keyword_scraper_test', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = p.communicate()
        # Splits the results based on automatically added characters
        keywords = output.splitlines()
        keywords = keywords[:len(keywords)-1]

        assert_list = ["nicolas", "cage"]
        for test in assert_list:
            self.assertIn(test, keywords, "Keyword " + test + " not found or frequent enough")

    def test_phone_number_scraper(self):
        # Runs the Test spider and pipes the printed output to "output"
        p = subprocess.Popen('scrapy crawl phone_number_scraper_test', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = p.communicate()
        # Splits the results based on automatically added characters
        numbers = output.splitlines()
        numbers = numbers[:len(numbers)-1]

        assert_list = ["0402026070", "9435134726"]
        for test in assert_list:
            self.assertIn(test, numbers, "Phone number " + str(test) + " not found")

if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0]:
            raise