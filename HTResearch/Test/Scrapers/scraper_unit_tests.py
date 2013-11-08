import unittest
import pickle
import os.path

from bson.binary import Binary

from HTResearch.WebCrawler.WebCrawler.scrapers.document_scrapers import *
from HTResearch.DataAccess.dto import URLMetadataDTO
from HTResearch.DataModel.model import URLMetadata
from HTResearch.Utilities.converter import DTOConverter


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
    def set_up_url_metadata_scraper_test(self):
        """Set up database for URLMetadataScraper test. Not called automatically"""
        urlmetadata = URLMetadata(
            url="http://www.google.com",
            last_visited=datetime(1, 1, 1),
            update_freq=5,
            score=0,
            checksum=Binary('154916369406075238760605425088915003118'),
        )
        urlmetadata2 = URLMetadata(
            checksum=Binary('199553381546012383114562002951261892300'),
            last_visited=datetime(1, 1, 1),
            update_freq=1,
            url='http://www.halftheskymovement.org/partners'
        )

        ctx = ApplicationContext(DAOContext())

        self.url_dto = DTOConverter.to_dto(URLMetadataDTO, urlmetadata)
        self.url_dto2 = DTOConverter.to_dto(URLMetadataDTO, urlmetadata2)
        self.url_dao = ctx.get_object("URLMetadataDAO")
        self.url_dao.create_update(self.url_dto)
        self.url_dao.create_update(self.url_dto2)

    def tear_down_url_metadata_scraper_test(self):
        """Undo setup to database for URLMetadataScraper test. Not called automatically"""
        self.url_dao.delete(self.url_dto)
        self.url_dao.delete(self.url_dto2)

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
        assert_list = ["sgnhrc@nic.in",
                       "covdnhrc@nic.in",
                       "anilpradhanshilong@gmail.com",
                       "snarayan1946@gmail.com",
                       "tvarghese@bombayteenchallenge.org"]

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

        assert_list = ["0402026070", "9435134726"]
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
            {'url': 'http://www.stoptrafficking.net/about', 'domain': 'stoptrafficking.net'},
            {'url': 'http://www.stoptrafficking.net/services/training', 'domain': 'stoptrafficking.net'},
            {'url': 'http://visit.unl.edu/', 'domain': 'unl.edu'},
            {'url': 'http://www.unl.edu/ucomm/prospective/', 'domain': 'unl.edu'},
        ]

        for test in assert_list:
            self.assertIn(test, links, "URL " + str(test) + " was not found")

    def test_org_name_scraper(self):
        test_files = [
            "httpbombayteenchallengeorg",
            "httpwwwprajwalaindiacomhomehtml",
            "httpwwwhalftheskymovementorg",
            "httpapneaaporg",
            "httpwwwbbaorgin",
            "httpwwwijmorg",
            "httpwwwtissedu",
        ]

        org_name_scraper = OrgNameScraper()
        names = []

        for input_file in test_files:
            response = file_to_response(input_file)
            if response is not None:
                ret = org_name_scraper.parse(response)
                if isinstance(ret, type([])):
                    names = names + ret
                else:
                    names.append(ret)

        assert_list = [
            "Bombay Teen Challenge",
            "PRAJWALA",
            "Half the Sky",
            "Apne Aap",
            "Bachpan Bachao Andolan",
            "Tata Institute of Social Sciences",
            "International Justice Mission",
        ]
        for test in assert_list:
            self.assertIn(test, names, 'Name \'' + test + '\' not found')

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

    def test_org_partners_scraper(self):
        test_files = [
            "httpwwwhalftheskymovementorgpartners",
            "httpwwwassetindiafoundationorgwhoweare",
            "httpapneaaporgaboutusourpartnersnetworks",
        ]

        org_partners_scraper = OrgPartnersScraper()
        partners = []

        for input_file in test_files:
            response = file_to_response(input_file)
            if response is not None:
                ret = org_partners_scraper.parse(response)
                if isinstance(ret, type([])):
                    partners += ret
                else:
                    partners.append(ret)

        partner_urls = map(lambda partner: partner['organization_url'], partners)

        # Make sure organizations with these URLs were found
        assert_list = [
            'www.acumenfund.org/',
            'www.afghaninstituteoflearning.org/',
            'www.prajwalaindia.com/',
            'www.mencanstoprape.org/',
            'novofoundation.org/',
        ]
        for test in assert_list:
            self.assertIn(test, partner_urls, 'Partner with URL %s not found' % test)

        # Make sure these urls were NOT found - they are not partner organizations
        assert_list = [
            'www.pbs.org/',
            'www.cpb.org/',
        ]
        for test in assert_list:
            self.assertNotIn(test, partner_urls, 'Invalid URL (not a partner org): %s' % test)

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
            'name': 'Bombay Teen Challenge',
            'types': [
                OrgTypesEnum.RELIGIOUS,
                OrgTypesEnum.EDUCATION,
                OrgTypesEnum.PREVENTION,
            ],
            'phone_numbers': [
                '16157124863',  # US number
                '912226042242'  # indian number
            ],
            'emails': [
                'tvarghese@bombayteenchallenge.org',
                'kkdevaraj@bombayteenchallenge.org',
            ],
            'address':
                'Mumbai 400052',
            'contacts': [
                # not yet implemented
            ],
            'organization_url': 'bombayteenchallenge.org/',
            'partners': [
                # not yet implemented
            ],
        }]

        for test in assert_list:
            self.assertIn(test, orgs, 'Org \'' + str(test) + '\' not found')

    def test_urlmetadata_scraper(self):
        self.set_up_url_metadata_scraper_test()

        test_files = [
            "httpbombayteenchallengeorg",
            "httpwwwgooglecom",
            "httpwwwhalftheskymovementorgpartners",
        ]

        url_mds = UrlMetadataScraper()
        scraped_urls = []

        for input_file in test_files:
            response = file_to_response(input_file)
            if response is not None:
                ret = url_mds.parse(response)
                if isinstance(ret, type([])):
                    scraped_urls = scraped_urls + ret
                else:
                    scraped_urls.append(ret)

        # We can't possibly get the last_visited time exactly right, so set to date
        for scraped_url in scraped_urls:
            scraped_url['last_visited'] = scraped_url['last_visited'].date()

        assert_list = [
            {
                'checksum': Binary('154916369406075238760605425088915003118'),
                'last_visited': datetime.now().date(),
                'update_freq': 0,
                'url': 'http://bombayteenchallenge.org/'
            },
            {
                'checksum': Binary('94565939257467841022060717122642335157'),
                'last_visited': datetime.now().date(),
                'update_freq': 6, # incremented one from setup b/c diff checksum
                'url': 'http://www.google.com'
            },
            {
                'checksum': Binary('199553381546012383114562002951261892300'),
                'last_visited': datetime.now().date(),
                'update_freq': 1,  # not incremented b/c checksum is same
                'url': 'http://www.halftheskymovement.org/partners'
            },
        ]

        # do teardown now in case of failure
        self.tear_down_url_metadata_scraper_test()

        for test in assert_list:
            self.assertIn(test, scraped_urls, 'Invalid URL Metadata Didn\'t Find: %s' % str(test))



if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0]:
            raise
