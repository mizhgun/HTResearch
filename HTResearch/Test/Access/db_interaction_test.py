# stdlib imports
import unittest
from springpython.context import ApplicationContext
from springpython.config import Object

# project imports
from HTResearch.DataModel.model import *
from HTResearch.Utilities.converter import DTOConverter
from HTResearch.Utilities.context import DAOContext
from HTResearch.Test.Mocks.dao import *
from HTResearch.DataModel.enums import AccountType


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


class DatabaseInteractionTest(unittest.TestCase):
    def setUp(self):
        print "New DatabaseInteractionTest running"

        self.contact = Contact(first_name="Jordan",
                               last_name="Degner",
                               email="jdegner0129@gmail.com")
        self.organization = Organization(name="Yee University",
                                         organization_url="http://com.bee.yee",
                                         contacts=[self.contact],
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
                                             total=10,
                                             references=[
                                                 PageRankVectorDTO(
                                                     org_domain='yoyodyne.com',
                                                     count=2,
                                                     pages=[
                                                         UrlCountPairDTO(
                                                             url='http://www.yoyodyne.com/',
                                                             count=2
                                                         )
                                                     ]
                                                 ),
                                                 PageRankVectorDTO(
                                                     org_domain='trystero.org',
                                                     count=4,
                                                     pages=[
                                                         UrlCountPairDTO(
                                                             url='http://www.yoyodyne.com/',
                                                             count=3
                                                         ),
                                                         UrlCountPairDTO(
                                                             url='http://www.yoyodyne.com/contacts.php',
                                                             count=1
                                                         )
                                                     ]
                                                 ),
                                                 PageRankVectorDTO(
                                                     org_domain='thurnandtaxis.info',
                                                     count=4,
                                                     pages=[
                                                         UrlCountPairDTO(
                                                             url='http://www.yoyodyne.com/',
                                                             count=4
                                                         )
                                                     ]
                                                 )
                                             ]
                                         )
        )
        self.publication = Publication(title="The Book of Yee",
                                       authors="Sam Adams, {0} {1}".format(self.contact.first_name,
                                                                           self.contact.last_name),
                                       publisher="{0} {1}".format(self.contact.first_name, self.contact.last_name))
        self.urlmetadata = URLMetadata(url="http://google.com")
        self.user = User(first_name="Bee", last_name="Yee",
                         email="beeyee@yee.com", password="iambeeyee",
                         background="I love bees and yees",
                         account_type=AccountType.COLLABORATOR)

        self.ctx = ApplicationContext(TestableDAOContext())

    def tearDown(self):
        with MockDBConnection() as db:
            db.dropall()

    def test_contact_dao(self):
        contact_dto = DTOConverter.to_dto(ContactDTO, self.contact)
        contact_dao = self.ctx.get_object("ContactDAO")

        print 'Testing contact creation ...'
        contact_dao.create_update(contact_dto)

        assert_contact = contact_dao.find(id=contact_dto.id,
                                          first_name=contact_dto.first_name,
                                          last_name=contact_dto.last_name,
                                          email=contact_dto.email)
        self.assertEqual(assert_contact.first_name, contact_dto.first_name)
        self.assertEqual(assert_contact.last_name, contact_dto.last_name)
        self.assertEqual(assert_contact.email, contact_dto.email)

        print 'Testing contact text search ...'

        assert_contacts = contact_dao.findmany(search='jordan degner',
                                               num_elements=10)
        self.assertEqual(len(assert_contacts), 1)
        self.assertEqual(assert_contacts[0].first_name, contact_dto.first_name)

        assert_contacts = contact_dao.findmany(search='bee yee', num_elements=10)
        self.assertEqual(len(assert_contacts), 0)

        assert_contacts = contact_dao.findmany(search='@gmail', search_fields=['email', ], num_elements=10)
        self.assertEqual(len(assert_contacts), 1)
        self.assertEqual(assert_contacts[0].first_name, contact_dto.first_name)

        print 'Testing contact editing ...'
        contact_dto.first_name = "Djordan"
        contact_dao.create_update(contact_dto)

        assert_contact = contact_dao.find(id=contact_dto.id,
                                          first_name=contact_dto.first_name)
        self.assertEqual(assert_contact.first_name, contact_dto.first_name)

        print 'Testing contact deletion ...'
        contact_dao.delete(contact_dto)

        assert_contact = contact_dao.find(id=contact_dto.id)
        self.assertTrue(assert_contact is None)

        print 'ContactDAO tests passed'

    def test_contact_dao_field_weights(self):
        print "Checking ContactDAO._field_weights for consistency with ContactDTO"
        contact_dto = DTOConverter.to_dto(ContactDTO, self.contact)
        contact_dao = self.ctx.get_object("ContactDAO")
        for key in contact_dto:
            if key == "id":
                continue
            self.assertIn(key, contact_dao._field_weights.keys(),
                          "ERROR: a field was added to DTO but not to _field_weights,"
                          "a member of ContactDAO")
        total = 0.0
        for key, value in contact_dao._field_weights.iteritems():
            total += value
        self.assertEqual(1.0, total, "ERROR: ContactDAO._field_weights do not add to 1.0")

    def test_organization_dao(self):
        org_dto = DTOConverter.to_dto(OrganizationDTO, self.organization)
        org_dao = self.ctx.get_object("OrganizationDAO")

        print 'Testing organization creation ...'
        org_dao.create_update(org_dto)

        assert_org = org_dao.find(id=org_dto.id,
                                  name=org_dto.name,
                                  organization_url=org_dto.organization_url,
                                  email_key=org_dto.email_key,
                                  emails=org_dto.emails,
                                  phone_numbers=org_dto.phone_numbers,
                                  facebook=org_dto.facebook,
                                  twitter=org_dto.twitter,
                                  address=org_dto.address,
                                  keywords=org_dto.keywords,
                                  types=org_dto.types[0],
        )
        self.assertEqual(assert_org.name, org_dto.name)
        self.assertEqual(assert_org.organization_url, org_dto.organization_url)
        self.assertEqual(assert_org.contacts, org_dto.contacts)
        self.assertEqual(assert_org.email_key, org_dto.email_key)
        self.assertEqual(assert_org.emails, org_dto.emails)
        self.assertEqual(assert_org.phone_numbers, org_dto.phone_numbers)
        self.assertEqual(assert_org.facebook, org_dto.facebook)
        self.assertEqual(assert_org.twitter, org_dto.twitter)
        self._compare_page_rank_info(assert_org, org_dto)

        print 'Testing organization text search ...'

        assert_orgs = org_dao.findmany(search='YeE university ers Religious govern secUTION ISFP Yeesy',
                                       num_elements=10)
        self.assertEqual(len(assert_orgs), 1)
        self.assertEqual(assert_orgs[0].name, org_dto.name)

        assert_orgs = org_dao.findmany(search='prevention advocacy', num_elements=10)
        self.assertEqual(len(assert_orgs), 0)

        assert_orgs = org_dao.findmany(search='religious', search_fields=['types', ], num_elements=10)
        self.assertEqual(len(assert_orgs), 1)
        self.assertEqual(assert_orgs[0].name, org_dto.name)

        assert_orgs = org_dao.findmany(search='ISFP', search_fields=['keywords', ], num_elements=10)
        self.assertEqual(len(assert_orgs), 1)

        assert_orgs = org_dao.findmany(search='omaha', search_fields=['address', ], num_elements=10)
        self.assertEqual(len(assert_orgs), 1)
        self.assertEqual(assert_orgs[0].name, org_dto.name)

        print 'Testing organization editing ...'
        org_dto.name = "Yee Universityee"
        org_dto.contacts = []
        org_dao.create_update(org_dto)

        assert_org = org_dao.find(id=org_dto.id,
                                  name=u'Yee Universityee')
        self.assertEqual(assert_org.name, org_dto.name)
        self.assertEqual(assert_org.organization_url, org_dto.organization_url)
        self.assertEqual(assert_org.contacts, org_dto.contacts)

        print 'Testing organization deletion ...'
        org_dao.delete(org_dto)

        assert_org = org_dao.find(id=org_dto.id)
        self.assertTrue(assert_org is None)

        print 'OrganizationDAO tests passed'

    def test_organization_dao_field_weights(self):
        print "Checking OrganizationDAO._field_weights for consistency with OrganizationDTO"
        org_dto = DTOConverter.to_dto(OrganizationDTO, self.organization)
        org_dao = self.ctx.get_object("OrganizationDAO")
        for key in org_dto:
            if key == "id":
                continue
            self.assertIn(key, org_dao._field_weights.keys(),
                          "ERROR: a field was added to DTO but not to _field_weights,"
                          "a member of OrganizationDAO")
        total = 0.0
        for key, value in org_dao._field_weights.iteritems():
            total += value
        self.assertEqual(1.0, total, "ERROR: OrganizationDAO._field_weights do not add to 1.0")

    def test_publication_dao(self):
        pub_dto = DTOConverter.to_dto(PublicationDTO, self.publication)
        pub_dao = self.ctx.get_object("PublicationDAO")

        print 'Testing publication creation ...'
        pub_dao.create_update(pub_dto)

        assert_pub = pub_dao.find(id=pub_dto.id,
                                  title=pub_dto.title)
        self.assertEqual(assert_pub.title, pub_dto.title)
        self.assertEqual(assert_pub.authors, pub_dto.authors)
        self.assertEqual(assert_pub.publisher, pub_dto.publisher)

        print 'Testing publication text search ...'

        assert_pubs = pub_dao.findmany(search='book of yee degner ADAMS',
                                       num_elements=10)
        self.assertEqual(len(assert_pubs), 1)
        self.assertEqual(assert_pubs[0].title, pub_dto.title)

        assert_pubs = pub_dao.findmany(search='nosuchpublication', num_elements=10)
        self.assertEqual(len(assert_pubs), 0)

        assert_pubs = pub_dao.findmany(search='sam adams', search_fields=['authors', ], num_elements=10)
        self.assertEqual(len(assert_pubs), 1)
        self.assertEqual(assert_pubs[0].title, pub_dto.title)

        print 'Testing publication editing ...'
        pub_dto.title = "The Book of Mee"
        pub_dao.create_update(pub_dto)

        assert_pub = pub_dao.find(id=pub_dto.id,
                                  title=pub_dto.title)
        self.assertEqual(assert_pub.title, pub_dto.title)

        print 'Testing publication deletion ...'
        pub_dao.delete(pub_dto)

        assert_pub = pub_dao.find(id=pub_dto.id)
        self.assertTrue(assert_pub is None)

        print 'PublicationDAO tests passed'

    def test_urlmetadata_dao(self):
        url_dto = DTOConverter.to_dto(URLMetadataDTO, self.urlmetadata)
        url_dao = self.ctx.get_object("URLMetadataDAO")

        print 'Testing URL creation ...'
        url_dao.create_update(url_dto)

        assert_url = url_dao.find(id=url_dto.id,
                                  url=url_dto.url)
        self.assertEqual(assert_url.url, url_dto.url)

        print 'Testing URL editing ...'
        url_dto.url = "http://facebook.com"
        url_dao.create_update(url_dto)

        assert_url = url_dao.find(id=url_dto.id,
                                  url=url_dto.url)
        self.assertEqual(assert_url.url, url_dto.url)

        print 'Testing URL deletion ...'
        url_dao.delete(url_dto)

        assert_url = url_dao.find(id=url_dto.id)
        self.assertTrue(assert_url is None)

        print 'URLMetadataDAO tests passed'

    def test_user_dao(self):
        user_dto = DTOConverter.to_dto(UserDTO, self.user)
        user_dao = self.ctx.get_object("UserDAO")

        print 'Testing user creation ...'
        user_dao.create_update(user_dto)

        assert_user = user_dao.find(id=user_dto.id)

        self.assertEqual(assert_user.id, user_dto.id)

        print 'Testing user editing ...'
        user_dto.first = "Byee"
        user_dto.last = "Ybee"

        user_dao.create_update(user_dto)

        assert_user = user_dao.find(id=user_dto.id)

        self.assertEqual(assert_user.id, user_dto.id)
        self.assertEqual(assert_user.first_name, user_dto.first_name)
        self.assertEqual(assert_user.last_name, user_dto.last_name)

        print 'Testing user deletion ...'
        user_dao.delete(user_dto)

        assert_user = user_dao.find(id=user_dto.id)
        self.assertTrue(assert_user is None)

        print 'UserDAO tests passed'

    def test_user_dao_field_weights(self):
        print "Checking UserDAO._field_weights for consistency with UserDTO"
        user_dto = DTOConverter.to_dto(UserDTO, self.user)
        user_dao = self.ctx.get_object("UserDAO")
        for key in user_dto:
            if key == "id":
                continue
            self.assertIn(key, user_dao._field_weights.keys(),
                          "ERROR: a field was added to DTO but not to _field_weights,"
                          "a member of UserDAO")
        total = 0.0
        for key, value in user_dao._field_weights.iteritems():
            total += value
        self.assertEqual(1.0, total, "ERROR: UserDAO._field_weights do not add to 1.0")

    def test_merge_records(self):
        contact_dto = DTOConverter.to_dto(ContactDTO, self.contact)
        contact_dao = self.ctx.get_object("ContactDAO")

        print 'Saving initial record ...'
        contact_dao.create_update(contact_dto)

        print 'Creating a duplicate and attempting an insert ...'
        new_contact = Contact(email="jdegner0129@gmail.com",
                              phones=['4029813230'])
        new_contact_dto = DTOConverter.to_dto(ContactDTO, new_contact)
        contact_dao.create_update(new_contact_dto)

        print 'Asserting that the old contact was updated'
        assert_contact = contact_dao.find(id=contact_dto.id)
        self.assertEqual(assert_contact.phones, new_contact_dto.phones)

        print 'Merge records tests passed'


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