# stdlib imports
import unittest
from springpython.context import ApplicationContext
from springpython.config import Object

# project imports
from HTResearch.DataModel.model import *
from HTResearch.Utilities.converter import DTOConverter
from HTResearch.Utilities.context import DAOContext
from HTResearch.Test.Mocks.dao import *
from HTResearch.DataModel.enums import OrgTypesEnum


class TestableDAOContext(DAOContext):
    @Object()
    def RegisteredDBConnection(self):
        return MockDBConnection

    @Object()
    def RegisteredContactDAO(self):
        return MockContactDAO

    @Object()
    def RegisteredOrganizationDAO(self):
        return MockOrganizationDAO

    @Object()
    def RegisteredPublicationDAO(self):
        return MockPublicationDAO

    @Object()
    def RegisteredURLMetadataDAO(self):
        return MockURLMetadataDAO

    @Object()
    def RegisteredGeocode(self):
        return lambda x: [0.0, 0.0]


class PageRankMergeTest(unittest.TestCase):
    def setUp(self):
        print "New PageRankMergeTest running"

        self.organization = Organization(name="Yee University",
                                         organization_url="www.yee.com",
                                         email_key="bee@yee.com",
                                         emails=["info@yee.com", "stuff@yee.com"],
                                         phone_numbers=[5555555555, "(555)555-5555"],
                                         facebook="http://www.facebook.com/yee",
                                         twitter="http://www.twitter.com/yee",
                                         address="5124 Yeesy Street Omaha, NE 68024",
                                         keywords="intj enfp entp isfp enfj istj",
                                         types=[OrgTypesEnum.RELIGIOUS,
                                                OrgTypesEnum.GOVERNMENT,
                                                OrgTypesEnum.PROSECUTION,
                                         ],
                                         page_rank_info=PageRankInfoDTO(
                                             total_with_self=10,
                                             total=8,
                                             references=[
                                                 PageRankVectorDTO(
                                                     org_domain='yee.com',
                                                     count=2,
                                                     pages=[
                                                         UrlCountPairDTO(
                                                             url='http://www.yee.com/',
                                                             count=2
                                                         )
                                                     ]
                                                 ),
                                                 PageRankVectorDTO(
                                                     org_domain='trystero.org',
                                                     count=4,
                                                     pages=[
                                                         UrlCountPairDTO(
                                                             url='http://www.yee.com/',
                                                             count=3
                                                         ),
                                                         UrlCountPairDTO(
                                                             url='http://www.yee.com/contacts.php',
                                                             count=1
                                                         )
                                                     ]
                                                 ),
                                                 PageRankVectorDTO(
                                                     org_domain='thurnandtaxis.info',
                                                     count=4,
                                                     pages=[
                                                         UrlCountPairDTO(
                                                             url='http://www.yee.com/',
                                                             count=4
                                                         )
                                                     ]
                                                 )
                                             ]
                                         )
        )

        self.ctx = ApplicationContext(TestableDAOContext())

    def tearDown(self):
        with MockDBConnection() as db:
            db.dropall()

    def test_page_rank_merge(self):
        org_dto = DTOConverter.to_dto(OrganizationDTO, self.organization)
        org_dao = self.ctx.get_object("OrganizationDAO")

        print 'Putting initial data in database'
        org_dao.create_update(org_dto)

        new_organization = OrganizationDTO(name="Yee University",
                                           organization_url="www.yee.com",
                                           page_rank_info=PageRankInfoDTO(
                                               total_with_self=18,
                                               total=16,
                                               references=[
                                                   PageRankVectorDTO(
                                                       org_domain='yee.com',
                                                       count=2,
                                                       pages=[
                                                           UrlCountPairDTO(
                                                               url='http://www.yee.com/test.php',
                                                               count=2
                                                           )
                                                       ]
                                                   ),
                                                   PageRankVectorDTO(
                                                       org_domain='trystero.org',
                                                       count=12,
                                                       pages=[
                                                           UrlCountPairDTO(
                                                               url='http://www.yee.com/',
                                                               count=2
                                                           ),
                                                           UrlCountPairDTO(
                                                               url='http://www.yee.com/contacts.php',
                                                               count=10
                                                           )
                                                       ]
                                                   ),
                                                   PageRankVectorDTO(
                                                       org_domain='philately.com',
                                                       count=4,
                                                       pages=[
                                                           UrlCountPairDTO(
                                                               url='http://www.yee.com/test.php',
                                                               count=4
                                                           )
                                                       ]
                                                   )
                                               ]
                                           )
        )

        test_org = Organization(name="Yee University",
                                organization_url="www.yee.com",
                                email_key="bee@yee.com",
                                emails=["info@yee.com", "stuff@yee.com"],
                                phone_numbers=[5555555555, "(555)555-5555"],
                                facebook="http://www.facebook.com/yee",
                                twitter="http://www.twitter.com/yee",
                                address="5124 Yeesy Street Omaha, NE 68024",
                                keywords="intj enfp entp isfp enfj istj",
                                types=[OrgTypesEnum.RELIGIOUS,
                                       OrgTypesEnum.GOVERNMENT,
                                       OrgTypesEnum.PROSECUTION,
                                ],
                                page_rank_info=PageRankInfoDTO(
                                    total_with_self=24,
                                    total=20,
                                    references=[
                                        PageRankVectorDTO(
                                            org_domain='yee.com',
                                            count=4,
                                            pages=[
                                                UrlCountPairDTO(
                                                    url='http://www.yee.com/',
                                                    count=2
                                                ),
                                                UrlCountPairDTO(
                                                    url='http://www.yee.com/test.php',
                                                    count=2
                                                )
                                            ]
                                        ),
                                        PageRankVectorDTO(
                                            org_domain='trystero.org',
                                            count=12,
                                            pages=[
                                                UrlCountPairDTO(
                                                    url='http://www.yee.com/',
                                                    count=2
                                                ),
                                                UrlCountPairDTO(
                                                    url='http://www.yee.com/contacts.php',
                                                    count=10
                                                )
                                            ]
                                        ),
                                        PageRankVectorDTO(
                                            org_domain='thurnandtaxis.info',
                                            count=4,
                                            pages=[
                                                UrlCountPairDTO(
                                                    url='http://www.yee.com/',
                                                    count=4
                                                )
                                            ]
                                        ),
                                        PageRankVectorDTO(
                                            org_domain='philately.com',
                                            count=4,
                                            pages=[
                                                UrlCountPairDTO(
                                                    url='http://www.yee.com/test.php',
                                                    count=4
                                                )
                                            ]
                                        )
                                    ]
                                )
        )

        print 'Merging new data'
        org_dao.create_update(new_organization)

        assert_org = org_dao.find(id=org_dto.id)

        self.assertEqual(assert_org.name, test_org.name)
        self.assertEqual(assert_org.organization_url, test_org.organization_url)
        self.assertEqual(assert_org.email_key, test_org.email_key)
        self.assertEqual(assert_org.emails, test_org.emails)
        self.assertEqual(assert_org.phone_numbers, test_org.phone_numbers)
        self.assertEqual(assert_org.facebook, test_org.facebook)
        self.assertEqual(assert_org.twitter, test_org.twitter)
        self._compare_page_rank_info(assert_org, test_org)

        print 'OrganizationDAO tests passed'

    def _compare_page_rank_info(self, org1, org2):
        page_rank_info1 = org1.page_rank_info
        page_rank_info2 = org2.page_rank_info
        self.assertEqual(page_rank_info1.total_with_self, page_rank_info2.total_with_self)
        self.assertEqual(page_rank_info1.total, page_rank_info2.total)
        self.assertEqual(len(page_rank_info2.references), len(page_rank_info1.references))
        for i in range(len(page_rank_info1.references)):
            ref1 = page_rank_info1.references[i]
            ref2 = page_rank_info2.references[i]
            self.assertEqual(ref1.org_domain, ref2.org_domain)
            self.assertEqual(ref1.count, ref2.count)
            self.assertEqual(len(ref1.pages), len(ref2.pages))
            for j in range(len(ref1.pages)):
                pair1 = ref1.pages[j]
                pair2 = ref2.pages[j]
                self.assertEqual(pair1.url, pair2.url)
                self.assertEqual(pair1.count, pair2.count)


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0]:
            raise
