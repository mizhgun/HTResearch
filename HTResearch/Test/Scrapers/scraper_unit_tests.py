import unittest
import pickle

from springpython.context import ApplicationContext
from springpython.config import Object

from HTResearch.Test.Mocks.utility_scrapers import *
from HTResearch.Utilities.context import DocumentScraperContext, UtilityScraperContext, UrlMetadataScraperContext
from HTResearch.WebCrawler.WebCrawler.scrapers.document_scrapers import *
from HTResearch.WebCrawler.WebCrawler.scrapers.link_scraper import PageRankScraper
from HTResearch.DataAccess.dto import URLMetadataDTO
from HTResearch.DataModel.model import URLMetadata
from HTResearch.Utilities.converter import DTOConverter
from HTResearch.Test.Mocks.connection import MockDBConnection
from HTResearch.Test.Mocks.dao import MockURLMetadataDAO
from HTResearch.Utilities.context import DAOContext


TEST_FILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')


class TestableDocumentScraperContext(DocumentScraperContext):
    @Object()
    def RegisteredContactNameScraper(self):
        return MockContactNameScraper

    @Object()
    def RegisteredEmailScraper(self):
        return MockEmailScraper

    @Object()
    def RegisteredIndianPhoneNumberScraper(self):
        return MockIndianPhoneNumberScraper

    @Object()
    def RegisteredKeywordScraper(self):
        return MockKeywordScraper

    @Object()
    def RegisteredOrgAddressScraper(self):
        return MockOrgAddressScraper

    @Object()
    def RegisteredOrgContactsScraper(self):
        return MockOrgContactsScraper

    @Object()
    def RegisteredOrgFacebookScraper(self):
        return MockOrgFacebookScraper

    @Object()
    def RegisteredOrgTwitterScraper(self):
        return MockOrgTwitterScraper

    @Object()
    def RegisteredOrgNameScraper(self):
        return MockOrgNameScraper

    @Object()
    def RegisteredOrgPartnersScraper(self):
        return MockOrgPartnersScraper

    @Object()
    def RegisteredOrgTypeScraper(self):
        return MockOrgTypeScraper

    @Object()
    def RegisteredOrgUrlScraper(self):
        return MockOrgUrlScraper

    @Object()
    def RegisteredFacebookScraper(self):
        return MockOrgFacebookScraper

    @Object()
    def RegisteredTwitterScraper(self):
        return MockOrgTwitterScraper

    @Object()
    def RegisteredPublicationAuthorsScraper(self):
        return MockPublicationAuthorsScraper

    @Object()
    def RegisteredPublicationDateScraper(self):
        return MockPublicationDateScraper

    @Object()
    def RegisteredPublicationPublisherScraper(self):
        return MockPublicationPublisherScraper

    @Object()
    def RegisteredPublicationTitleScraper(self):
        return MockPublicationTitleScraper

    @Object()
    def RegisteredPublicationTypeScraper(self):
        return MockPublicationTypeScraper

    @Object()
    def RegisteredUrlMetadataScraper(self):
        return MockUrlMetadataScraper

    @Object()
    def RegisteredUSPhoneNumberScraper(self):
        return MockUSPhoneNumberScraper


class TestableUrlMetadataScraperContext(UrlMetadataScraperContext):
    @Object()
    def RegisteredURLMetadataDAO(self):
        return MockURLMetadataDAO


class TestableUtilityScraperContext(UtilityScraperContext):
    @Object()
    def RegisteredKeywordScraper(self):
        return MockKeywordScraper


class TestableDAOContext(DAOContext):
    @Object()
    def RegisteredDBConnection(self):
        return MockDBConnection


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

        ctx = ApplicationContext(TestableDAOContext())

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
            "httpnhrcnicinContactUshtm",
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
        assert_list = [  # from first site, US names
                         {'name': "Gloria Steinem"},
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
                         {'name': "Pallavi Shardul Shroff"},
                         {'name': "Sujata Prasad"},
                         {'name': "Suresh Neotia"},
                         {'name': "Lata Bajoria"},
                         {'name': "Raju Bharat"},
                         {'name': "Manish Agarwal"},
                         {'name': "Lela Goren"},
                         {'name': "Ellyson Perkins"},
                         {'name': "Mona Sinha"},
                         # from second site, Indian names
                         {'name': 'Rishi Prakash'},
                         {'name': 'Vinod Seth'},
                         {'name': 'S K Gandhi'},
                         {'name': 'M S Gill'},
                         {'name': 'Chandra Kant Tyagi'},
                         {'name': 'Pooran Chandra Joshi'},
                         {'name': 'K P Singh'},
                         {'name': 'KHC Rao'},
                         {'name': 'Ajay Kumar'},
                         {'name': 'S. Narayan'},
                         {'name': 'S. Jalaja'},
                         {'name': 'R. Krishnamurthy'},
                         {'name': 'Mukesh Kumar'},
                         {'name': 'Jaimini Kumar Srivastava'},
                         {'name': 'Utpal Narayan Sarkar'},
                         {'name': 'Shoba George'},
                         {'name': 'Om Prakash'},
                         {'name': 'S K Shukla'},
                         {'name': 'Sudhir Chopra'},
                         {'name': 'C P Gupta'}]

        for test in assert_list:
            self.assertIn(test, names, 'Name {0} not found'.format(str(test)))


    def test_email_scraper(self):
        test_files = [
            "httpnhrcnicinContactUshtm",
            "httpbombayteenchallengeorg",
            "httpwwwtisseduTopMenuBarcontactuslocation1",
            "httpapneaaporgcontact",
            "httpsetbeautifulfreeorg"
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
                       "tvarghese@bombayteenchallenge.org",
                       "kkdevaraj@bombayteenchallenge.org"]

        for test in assert_list:
            self.assertIn(test, emails, 'Email {0} not found'.format(str(test)))

        # Make sure these aren't in the list
        assert_not_list = ["ajax-loader@2x.gif"]

        for test in assert_not_list:
            self.assertNotIn(test, emails, '{0} should not be found'.format(str(test)))

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
        keywords = ''

        for input_file in test_files:
            response = file_to_response(input_file)
            if response is not None:
                ret = keyword_scraper.parse(response)
                if isinstance(ret, type('')):
                    keywords += ' ' + ret

        assert_list = ["nicolas", "cage"]
        for test in assert_list:
            self.assertIn(test, keywords, "Keyword " + test + " not found or frequent enough")

    def test_link_scraper(self):
        test_files = [
            "httpwwwstoptraffickingnet",
            "httpnewsunledunewsroomsunltoday",
            "httpespngocomespnradiodallasplay",
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
            {
                'url': 'http://www.stoptrafficking.net/about',
                'domain': 'stoptrafficking.net',
                'last_visited': datetime(1, 1, 1, 0, 0),
            },
            {
                'url': 'http://www.stoptrafficking.net/services/training',
                'domain': 'stoptrafficking.net',
                'last_visited': datetime(1, 1, 1, 0, 0),
            },
            {
                'url': 'http://visit.unl.edu/',
                'domain': 'unl.edu',
                'last_visited': datetime(1, 1, 1, 0, 0),
            },
            {
                'url': 'http://www.unl.edu/ucomm/prospective/',
                'domain': 'unl.edu',
                'last_visited': datetime(1, 1, 1, 0, 0),
            },
        ]

        for test in assert_list:
            self.assertIn(test, links, "URL " + str(test) + " was not found")

    def test_org_fb_scraper(self):
        test_files = [
            "httpbombayteenchallengeorg",
            "httpwwwprajwalaindiacomhomehtml",
            "httpwwwhalftheskymovementorgpagesabouthalftheskymovement",
            "httpapneaaporg",

        ]

        org_fb_scraper = OrgFacebookScraper()
        facebook_links = []

        for input_file in test_files:
            response = file_to_response(input_file)
            if response is not None:
                ret = org_fb_scraper.parse(response)
                if isinstance(ret, list):
                    facebook_links = facebook_links + ret
                else:
                    facebook_links.append(ret)

        assert_list = [
            "http://www.facebook.com/BombayTeenChallenge",
            "https://www.facebook.com/sunitha.krishnan.33?ref=ts",
            "https://www.facebook.com/HalftheGame",
            "http://www.facebook.com/apneaap",
        ]

        for test in assert_list:
            self.assertIn(test, facebook_links, "Facebook link (" + test + ") not found")

    def test_org_twitter_scraper(self):
        test_files = [
            "httpbombayteenchallengeorg",
            "httpwwwprajwalaindiacomhomehtml",
            "httpwwwhalftheskymovementorgpagesabouthalftheskymovement",
            "httpapneaaporg",
        ]

        org_tw_scraper = OrgTwitterScraper()
        twitter_links = []

        for input_file in test_files:
            response = file_to_response(input_file)
            if response is not None:
                ret = org_tw_scraper.parse(response)
                if isinstance(ret, list):
                    twitter_links = twitter_links + ret
                else:
                    twitter_links.append(ret)

        assert_list = [
            'https://twitter.com/bombaytc',
            None,
            'https://twitter.com/#!/half',
            'http://www.twitter.com/apneaap'
        ]

        for test in assert_list:
            self.assertIn(test, twitter_links, "Twitter link (" + str(test) + ") not found")

    def test_org_name_scraper(self):
        test_files = [
            "httpbombayteenchallengeorg",
            "httpwwwprajwalaindiacomhomehtml",
            "httpwwwhalftheskymovementorgpagesabouthalftheskymovement",
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
        ctx = ApplicationContext(TestableUtilityScraperContext())
        test_files = [
            "httpbombayteenchallengeorg",
            "httpwwwnsagov",
            "httpwwwhalftheskymovementorgpagesabouthalftheskymovement",
        ]

        org_type_scraper = ctx.get_object('OrgTypeScraper')
        types = []

        for input_file in test_files:
            response = file_to_response(input_file)
            if response is not None:
                ret = org_type_scraper.parse(response)
                if isinstance(ret, type([])):
                    types = types + ret
                else:
                    types.append(ret)
        assert_list = [OrgTypesEnum.RELIGIOUS, OrgTypesEnum.GOVERNMENT, OrgTypesEnum.PREVENTION,
                       OrgTypesEnum.PROTECTION]
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

    def test_page_rank_info_scraper(self):
        test_files = [
            "httpwwwstoptraffickingnet",
            "httpnewsunledunewsroomsunltoday",
            "httpespngocomespnradiodallasplay",
        ]

        pri_scraper = PageRankScraper()
        infos = []

        for input_file in test_files:
            response = file_to_response(input_file)
            if response is not None:
                ret = pri_scraper.parse(response)
                if isinstance(ret, type([])):
                    infos = infos + ret
                else:
                    infos.append(ret)

        assert_list = [
            {
                'total': 0,
                'total_with_self': 13,
                'references': [
                    {
                        'count': 13,
                        'org_domain': 'stoptrafficking.net',
                        'pages': [
                            {
                                'count': 13,
                                'url': 'http://www.stoptrafficking.net/'
                            }
                        ]
                    }
                ]
            },
            {
                'total': 16,
                'total_with_self': 89,
                'references': [
                    {
                        'count': 73,
                        'org_domain': 'unl.edu',
                        'pages': [
                            {
                                'count': 73,
                                'url': 'http://news.unl.edu/newsrooms/unltoday/'
                            }
                        ]
                    },
                    {
                        'count': 1,
                        'org_domain': 'weather.gov',
                        'pages': [
                            {
                                'count': 1,
                                'url': 'http://news.unl.edu/newsrooms/unltoday/'
                            }
                        ]
                    },
                    {
                        'count': 1,
                        'org_domain': 'nufoundation.org',
                        'pages': [
                            {
                                'count': 1,
                                'url': 'http://news.unl.edu/newsrooms/unltoday/'
                            }
                        ]
                    },
                    {
                        'count': 2,
                        'org_domain': 'nebraska.edu',
                        'pages': [
                            {
                                'count': 2,
                                'url': 'http://news.unl.edu/newsrooms/unltoday/'
                            }
                        ]
                    },
                    {
                        'count': 1,
                        'org_domain': 'nutechventures.org',
                        'pages': [
                            {
                                'count': 1,
                                'url': 'http://news.unl.edu/newsrooms/unltoday/'
                            }
                        ]
                    },
                    {
                        'count': 1,
                        'org_domain': 'meltycampus.fr',
                        'pages': [
                            {
                                'count': 1,
                                'url': 'http://news.unl.edu/newsrooms/unltoday/'
                            }
                        ]
                    },
                    {
                        'count': 1,
                        'org_domain': 'kbia.org',
                        'pages': [
                            {
                                'count': 1,
                                'url': 'http://news.unl.edu/newsrooms/unltoday/'
                            }
                        ]
                    },
                    {
                        'count': 1,
                        'org_domain': 'cbslocal.com',
                        'pages': [
                            {
                                'count': 1,
                                'url': 'http://news.unl.edu/newsrooms/unltoday/'
                            }
                        ]
                    },
                    {
                        'count': 1,
                        'org_domain': 'insidehighered.com',
                        'pages': [
                            {
                                'count': 1,
                                'url': 'http://news.unl.edu/newsrooms/unltoday/'
                            }
                        ]
                    },
                    {
                        'count': 2,
                        'org_domain': 'twitter.com',
                        'pages': [
                            {
                                'count': 2,
                                'url': 'http://news.unl.edu/newsrooms/unltoday/'
                            }
                        ]
                    },
                    {
                        'count': 1,
                        'org_domain': 'huskers.com',
                        'pages': [
                            {
                                'count': 1,
                                'url': 'http://news.unl.edu/newsrooms/unltoday/'
                            }
                        ]
                    },
                    {
                        'count': 1,
                        'org_domain': 'huskeralum.org',
                        'pages': [
                            {
                                'count': 1,
                                'url': 'http://news.unl.edu/newsrooms/unltoday/'
                            }
                        ]
                    },
                    {
                        'count': 1,
                        'org_domain': 'facebook.com',
                        'pages': [
                            {
                                'count': 1,
                                'url': 'http://news.unl.edu/newsrooms/unltoday/'
                            }
                        ]
                    },
                    {
                        'count': 1,
                        'org_domain': 'cic.net',
                        'pages': [
                            {
                                'count': 1,
                                'url': 'http://news.unl.edu/newsrooms/unltoday/'
                            }
                        ]
                    },
                    {
                        'count': 1,
                        'org_domain': 'bigten.org',
                        'pages': [
                            {
                                'count': 1,
                                'url': 'http://news.unl.edu/newsrooms/unltoday/'
                            }
                        ]
                    },
                ]
            },
            None
        ]

        for test in assert_list:
            self.assertIn(test, infos, "URL " + str(test) + " was not found")

    def test_contact_scraper(self):
        ctx = ApplicationContext(TestableDocumentScraperContext())

        test_files = [
            "httpwwwprajwalaindiacomcontactushtml",
        ]

        contact_scraper = ctx.get_object('ContactScraper')
        contacts = []

        for input_file in test_files:
            response = file_to_response(input_file)
            if response is not None:
                ret = contact_scraper.parse(response)
                if isinstance(ret, type([])):
                    contacts = contacts + ret
                else:
                    contacts.append(ret)

        assert_list = [{
                           'email': 'test',
                           'first_name': 'test',
                           'last_name': 'test',
                           'organization': {'name': 'test'},
                           'position': 'test',
                           'phones': ['test'],
                       }]

        for test in assert_list:
            self.assertIn(test, contacts, 'Contact \'' + str(test) + '\' not found')

    def test_organization_scraper(self):
        ctx = ApplicationContext(TestableDocumentScraperContext())

        test_files = [
            "httpbombayteenchallengeorg",
        ]

        organization_scraper = ctx.get_object("OrganizationScraper")
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
                           "name": "test",
                           "types": ["test"],
                           "phone_numbers": ["test", "test"],
                           "emails": ["test"],
                           "address": "test",
                           "contacts": ["test test"],
                           "organization_url": 'http://bombayteenchallenge.org/',
                           "partners": ['test'],
                           "facebook": 'test',
                           "twitter": 'test',
                           "keywords":
                               "bombay challenge teen seek mumbai education woman health india life music read rescued "
                               "street vocational program  blog btc care child contact district donate drug gift light "
                               "live men office reach red safe tel training trust wa addict 501c3 access afraid allows "
                               "ambedkar announced ash bandra beauty began betrayed bound",
                       }]

        for test in assert_list:
            self.assertIn(test, orgs, 'Org \'' + str(test) + '\' not found')

    def test_urlmetadata_scraper(self):
        ctx = ApplicationContext(TestableUrlMetadataScraperContext())

        self.set_up_url_metadata_scraper_test()

        test_files = [
            "httpbombayteenchallengeorg",
            "httpwwwgooglecom",
            "httpwwwhalftheskymovementorgpartners",
        ]

        url_mds = ctx.get_object("UrlMetadataScraper")
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
                'last_visited': datetime.utcnow().date(),
                'update_freq': 0,
                'url': 'http://bombayteenchallenge.org/'
            },
            {
                'checksum': Binary('94565939257467841022060717122642335157'),
                'last_visited': datetime.utcnow().date(),
                'update_freq': 6,  # incremented one from setup b/c diff checksum
                'url': 'http://www.google.com'
            },
            {
                'checksum': Binary('199553381546012383114562002951261892300'),
                'last_visited': datetime.utcnow().date(),
                'update_freq': 1,  # not incremented b/c checksum is same
                'url': 'http://www.halftheskymovement.org/partners'
            },
        ]

        # do teardown now in case of failure
        self.tear_down_url_metadata_scraper_test()

        for test in assert_list:
            self.assertIn(test, scraped_urls, 'Invalid URL Metadata Didn\'t Find: %s' % str(test))

    def test_publication_citation_source_scraper(self):
        test_files = [
            "httpscholargooglecomscholarhlenqpaulbtnGassdt12C28",
        ]

        pub_scraper = PublicationCitationSourceScraper()
        sources = []

        for input_file in test_files:
            response = file_to_response(input_file)
            if response is not None:
                ret = pub_scraper.parse(response)
                if isinstance(ret, list):
                    sources = sources + ret
                else:
                    sources.append(ret)

        assert_list = [
            'FD5U1mFUAe8J', 'GouvW1uXQv4J', 'A_punTK0il4J', '09vlKiKyzVMJ', '1MI5x95WVlIJ', '5RnnsNt0VwwJ',
            'HZXqLOywHBMJ', '_mfiSSkjBDMJ', 'hjmy2wt_cq8J', 'qoyC2e35yt4J'
        ]

        for test in assert_list:
            self.assertIn(test, sources, "Publication source (" + test + ") not found")


    def test_publication_author_scraper(self):
        test_files = [
            "httpscholargooglecomscholarqinfoGouvW1uXQv4Jscholargooglecomoutputcitescirp0hlen",
        ]

        pub_scraper = PublicationAuthorsScraper()
        pubs = []

        for input_file in test_files:
            response = file_to_response(input_file)
            if response is not None:
                ret = pub_scraper.parse(response)
                print ret
                if isinstance(ret, list):
                    pubs = pubs + ret
                else:
                    pubs.append(ret)

        assert_list = [
            'Willis, Paul E.'
        ]

        for test in assert_list:
            self.assertIn(test, pubs, "Author set: (" + test + ") not found")


    def test_publication_date_scraper(self):
        test_files = [
            "httpscholargooglecomscholarqinfoGouvW1uXQv4Jscholargooglecomoutputcitescirp0hlen",
        ]

        pub_scraper = PublicationDateScraper()
        pubs = []

        for input_file in test_files:
            response = file_to_response(input_file)
            if response is not None:
                ret = pub_scraper.parse(response)
                print ret
                if isinstance(ret, list):
                    pubs = pubs + ret
                else:
                    pubs.append(ret)

        assert_list = [
            '1977'
        ]

        for test in assert_list:
            self.assertIn(test, pubs, "Date (" + test + ") not found")


    def test_publication_title_scraper(self):
        test_files = [
            "httpscholargooglecomscholarqinfoGouvW1uXQv4Jscholargooglecomoutputcitescirp0hlen",
        ]

        pub_scraper = PublicationTitleScraper()
        pubs = []

        for input_file in test_files:
            response = file_to_response(input_file)
            if response is not None:
                ret = pub_scraper.parse(response)
                print ret
                if isinstance(ret, list):
                    pubs = pubs + ret
                else:
                    pubs.append(ret)

        assert_list = [
            'Learning to labour: How working class kids get working class jobs'
        ]

        for test in assert_list:
            self.assertIn(test, pubs, "Title (" + test + ") not found")

    def test_publication_publisher_scraper(self):
        test_files = [
            "httpscholargooglecomscholarqinfoGouvW1uXQv4Jscholargooglecomoutputcitescirp0hlen",
        ]

        pub_scraper = PublicationPublisherScraper()
        pubs = []

        for input_file in test_files:
            response = file_to_response(input_file)
            if response is not None:
                ret = pub_scraper.parse(response)
                print ret
                if isinstance(ret, list):
                    pubs = pubs + ret
                else:
                    pubs.append(ret)

        assert_list = [
            'Columbia University Press'
        ]

        for test in assert_list:
            self.assertIn(test, pubs, "Publisher (" + test + ") not found")

    def test_publication_url_scraper(self):
        test_files = [
            "httpscholargooglecomscholarhlenqpaulbtnGassdt12C28",
        ]

        pub_scraper = PublicationURLScraper()
        pubs = []
        pub_scraper.seed_titles(['Learning to labour: How working class kids get working class jobs'])

        for input_file in test_files:
            response = file_to_response(input_file)
            if response is not None:
                ret = pub_scraper.parse(response)
                print ret
                if isinstance(ret, list):
                    pubs = pubs + ret
                else:
                    pubs.append(ret)

        assert_list = [
            'http://books.google.com/books?hl=en&amp;lr=&amp;id=3zmVaLrGIDEC&amp;oi=fnd&amp;pg=PR7&amp;dq=paul&amp;ots=7gy4pwXnwR&amp;sig=l5JsyyhbmZ7izyW7fNiYeBBDd1s'
        ]

        for test in assert_list:
            self.assertIn(test, pubs, "URL (" + test + ") not found")


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0]:
            raise
