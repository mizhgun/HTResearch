import unittest
import pickle

import os.path

from HTResearch.WebCrawler.WebCrawler.scrapers.document_scrapers import *
from HTResearch.WebCrawler.WebCrawler.scrapers.link_scraper import *

TEST_FILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')


def file_to_response(test_file):
    """Convert filename to the scrapy.http.Response stored object"""
    fullpath = os.path.join(TEST_FILE_DIR, test_file)
    if os.path.isfile(fullpath):
        with open(fullpath, mode='r') as input_file:
            return pickle.load(input_file)
    else:
        return None


class ScraperTests(unittest.TestCase):
    def test_address_scraper(self):
        test_files = [
            "httpwwwtisseduTopMenuBarcontactuslocation1",
            "httpapneaaporgcontact",
            "httpbombayteenchallengeorg",
            "httpwwwcompliancematterscomhumantrafficking",
            "httpwwwbbaorginqcontentcontactus",
            "httpwwwprajwalaindiacomhomehtml"
        ]

        addr_scraper = OrgAddressScraper()
        addresses = []

        for input_file in test_files:
            response = file_to_response(input_file)
            if response is not None:
                ret = addr_scraper.parse(response)
                if isinstance(ret, type([])):
                    addresses = addresses + ret
                else:
                    addresses.append(ret)

        # Hardcoded results based on the sites that were crawled
        assert_list = ["Guwahati 781001",
                       "New Delhi 110003",
                       "Hyderabad 500002",
                       "Mumbai 400064",
                       "New Delhi 110019",
                       "Mumbai 400052",
        ]

        for test in assert_list:
            self.assertIn(test, addresses, str(test) + " not found")

    def test_contact_name_scraper(self):
        test_files = [
            "httpapneaaporgaboutusourboard",
        ]

        contact_name_scraper = ContactNameScraper()
        names = []

        for input_file in test_files:
            response = file_to_response(input_file)
            if response is not None:
                ret = contact_name_scraper.parse(response)
                if isinstance(ret, type([])):
                    names = names + ret
                else:
                    names.append(ret)

        # Hardcoded results based on the sites that were crawled
        assert_list = [{'name': "Gloria Steinem"},
                       {'name': "Jennifer Buffett"},
                       {'name': "Peter Buffett"},
                       {'name': "Vishakha Desai"},
                       {'name': "Leslie Bluhm"},
                       {'name': "Judy Gold"},
                       {'name': "Ashley Judd"},
                       {'name': "Jounghoon Lee"},
                       {'name': "Pamela Shifman"},
                       {'name': "Lekha Poddar"},
                       {'name': "Namita Saraf"},
                       {'name': "Nayantara Palchoudhuri"},
                       {'name': "Pallavi Shroff"},
                       {'name': "Sujata Prasad"},
                       {'name': "Suresh Neotia"},
                       {'name': "Lata Bajoria"},
                       {'name': "Raju Bharat"},
                       {'name': "Manish Agarwal"},
                       {'name': "Lela Goren"},
                       {'name': "Ellyson Perkins"},
                       {'name': "Mona Sinha"},
        ]

        for test in assert_list:
            self.assertIn(test, names, 'Name {0} not found'.format(str(test)))

    def test_email_scraper(self):
        test_files = [
            "httpnhrcnicinContactUshtm",
            "httpbombayteenchallengeorg",
            "httpwwwtisseduTopMenuBarcontactuslocation1",
            "httpapneaaporgcontact",
        ]

        email_scraper = EmailScraper()
        emails = []

        for input_file in test_files:
            response = file_to_response(input_file)
            if response is not None:
                ret = email_scraper.parse(response)
                if isinstance(ret, type([])):
                    emails = emails + ret
                else:
                    emails.append(ret)

        # Hardcoded results based on the sites that were crawled
        assert_list = [{'email': "sgnhrc@nic.in"},
                       {'email': "covdnhrc@nic.in"},
                       {'email': "anilpradhanshilong@gmail.com"},
                       {'email': "snarayan1946@gmail.com"},
                       {'email': "tvarghese@bombayteenchallenge.org"}]

        for test in assert_list:
            self.assertIn(test, emails, 'Email {0} not found'.format(str(test)))

    def test_indian_phone_number_scraper(self):
        test_files = [
            "httpwwwstoptraffickinginDirectoryaspx",
        ]

        indian_phone_scraper = IndianPhoneNumberScraper()
        numbers = []

        for input_file in test_files:
            response = file_to_response(input_file)
            if response is not None:
                ret = indian_phone_scraper.parse(response)
                if isinstance(ret, type([])):
                    numbers = numbers + ret
                else:
                    numbers.append(ret)

        assert_list = [{'phone_number': "0402026070"}, {'phone_number': "9435134726"}]
        for test in assert_list:
            self.assertIn(test, numbers, "Phone number " + str(test) + " not found")

    def test_keyword_scraper(self):
        test_files = [
            "httpenwikipediaorgwikiNicolasCage",
        ]

        keyword_scraper = KeywordScraper()
        keywords = []

        for input_file in test_files:
            response = file_to_response(input_file)
            if response is not None:
                ret = keyword_scraper.parse(response)
                if isinstance(ret, type([])):
                    keywords = keywords + ret
                else:
                    keywords.append(ret)

        assert_list = ["nicolas", "cage"]
        for test in assert_list:
            self.assertIn(test, keywords, "Keyword " + test + " not found or frequent enough")

    def test_link_scraper(self):
        test_files = [
            "httpwwwstoptraffickingnet",
            "httpnewsunledunewsroomsunltoday",
            ]

        link_scraper = LinkScraper()
        links = []

        for input_file in test_files:
            response = file_to_response(input_file)
            if response is not None:
                ret = link_scraper.parse(response)
                if isinstance(ret, type([])):
                    links = links + ret
                else:
                    links.append(ret)

        assert_list = [
            {'url': 'http://www.stoptrafficking.net/about'},
            {'url': 'http://www.stoptrafficking.net/services/training'},
            {'url': 'http://visit.unl.edu/'},
            {'url': 'http://www.unl.edu/ucomm/prospective/'},
        ]

        for test in assert_list:
            self.assertIn(test, links, "URL " + str(test) + " was not found")

    def test_org_type_scraper(self):
        test_files = [
            "httpbombayteenchallengeorg",
            "httpwwwnsagov",
            "httpwwwhalftheskymovementorg",
        ]

        org_type_scraper = OrgTypeScraper()
        types = []

        for input_file in test_files:
            response = file_to_response(input_file)
            if response is not None:
                ret = org_type_scraper.parse(response)
                if isinstance(ret, type([])):
                    types = types + ret
                else:
                    types.append(ret)

        assert_list = [OrgTypesEnum.RELIGIOUS, OrgTypesEnum.GOVERNMENT, OrgTypesEnum.PROTECTION]
        for test in assert_list:
            self.assertIn(test, types, 'Type \'' + OrgTypesEnum.reverse_mapping[test] + '\' not found')

    def test_organization_scraper(self):
        test_files = [
            "httpbombayteenchallengeorg",
        ]

        organization_scraper = OrganizationScraper()
        orgs = []

        for input_file in test_files:
            response = file_to_response(input_file)
            if response is not None:
                ret = organization_scraper.parse(response)
                if isinstance(ret, type([])):
                    orgs = orgs + ret
                else:
                    orgs.append(ret)

        assert_list = [{
            'name': None, #'Bombay Teen Challenge', # not yet implemented
            'types': [
                OrgTypesEnum.RELIGIOUS,
                OrgTypesEnum.EDUCATION,
                OrgTypesEnum.PREVENTION,
            ],
            'phone_number': [
                {'phone_number': '16157124863'},
                #{'phone_number': '912226042242'}, # Indian phone number for BTC not currently found by Indian phone number scraper
            ],
            'email': [
                {'email': 'tvarghese@bombayteenchallenge.org'},
                {'email': 'kkdevaraj@bombayteenchallenge.org'},
            ],
            'address':
                'Mumbai 400052',
            'contacts': [
                # not yet implemented
            ],
            'organization_url': 'http://bombayteenchallenge.org/',
            'partners': [
                # not yet implemented
            ],
        }]

        for test in assert_list:
            self.assertIn(test, orgs, 'Org \'' + str(test) + '\' not found')


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0]:
            raise