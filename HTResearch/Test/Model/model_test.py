# stdlib imports
import unittest
from springpython.context import ApplicationContext
from springpython.config import Object

# project imports
from HTResearch.DataAccess.dto import ContactDTO, OrganizationDTO
from HTResearch.Utilities.converter import DTOConverter
from HTResearch.DataModel.enums import OrgTypesEnum
from HTResearch.DataModel.model import Contact, Organization, PageRankInfo, PageRankVector, UrlCountPair
from HTResearch.Utilities.context import ConverterContext
from HTResearch.Test.Mocks.dao import MockOrganizationDAO
from HTResearch.WebCrawler.WebCrawler.items import ScrapedContact


class TestableDAOContext(ConverterContext):
    @Object()
    def RegisteredOrganizationDAO(self):
        return MockOrganizationDAO


class ModelTest(unittest.TestCase):
    def test_org_dto_converter(self):
        my_org = Organization(name='Yoyodyne, Inc.',
                              address="1234 Yoyodyne Way, San Narciso, CA",
                              types=[OrgTypesEnum.GOVERNMENT, OrgTypesEnum.RESEARCH],
                              phone_numbers=["4026170423"],
                              emails=["info@yoyodyne.com"],
                              contacts=[],
                              organization_url="www.yoyodyne.com",
                              page_rank_info=PageRankInfo(
                                  total_with_self=10,
                                  total=8,
                                  references=[
                                      PageRankVector(
                                          org_domain='yoyodyne.com',
                                          count=2,
                                          pages=[
                                              UrlCountPair(
                                                  url='http://www.yoyodyne.com/',
                                                  count=2
                                              )
                                          ]
                                      ),
                                      PageRankVector(
                                          org_domain='trystero.org',
                                          count=4,
                                          pages=[
                                              UrlCountPair(
                                                  url='http://www.yoyodyne.com/',
                                                  count=3
                                              ),
                                              UrlCountPair(
                                                  url='http://www.yoyodyne.com/contacts.php',
                                                  count=1
                                              )
                                          ]
                                      ),
                                      PageRankVector(
                                          org_domain='thurnandtaxis.info',
                                          count=4,
                                          pages=[
                                              UrlCountPair(
                                                  url='http://www.yoyodyne.com/',
                                                  count=4
                                              )
                                          ]
                                      )
                                  ]
                              )
        )

        print 'Converting an organization model to a DTO.'
        org_dto = DTOConverter.to_dto(OrganizationDTO, my_org)

        print 'Testing equality...'
        for attr, value in my_org.__dict__.iteritems():
            if attr == 'page_rank_info':
                self._compare_page_rank_info(my_org, org_dto)
            else:
                self.assertEqual(getattr(my_org, attr), getattr(org_dto, attr),
                                 "{0} attribute not equal".format(attr))

        print 'Converting a DTO to an organization.'
        my_org = DTOConverter.from_dto(Organization, org_dto)

        print 'Testing equality...'
        for attr, value in my_org.__dict__.iteritems():
            if attr == 'page_rank_info':
                self._compare_page_rank_info(my_org, org_dto)
            else:
                self.assertEqual(getattr(my_org, attr), getattr(org_dto, attr),
                                 "{0} attribute not equal".format(attr))

    def _compare_page_rank_info(self, org_model, org_dto):
        page_rank_info_model = getattr(org_model, 'page_rank_info')
        page_rank_info_dto = getattr(org_dto, 'page_rank_info')
        self.assertEqual(page_rank_info_model.total_with_self, page_rank_info_dto.total_with_self)
        self.assertEqual(page_rank_info_model.total, page_rank_info_dto.total)
        self.assertEqual(len(page_rank_info_dto.references), len(page_rank_info_model.references))
        for i in range(len(page_rank_info_model.references)):
            ref_model = page_rank_info_model.references[i]
            ref_dto = page_rank_info_dto.references[i]
            self.assertEqual(ref_model.org_domain, ref_dto.org_domain)
            self.assertEqual(ref_model.count, ref_dto.count)
            self.assertEqual(len(ref_model.pages), len(ref_dto.pages))
            for j in range(len(ref_model.pages)):
                pair_model = ref_model.pages[j]
                pair_dto = ref_dto.pages[j]
                self.assertEqual(pair_model.url, pair_dto.url)
                self.assertEqual(pair_model.count, pair_dto.count)

    def test_contact_dto_converter(self):
        my_contact = Contact(first_name="Jordan",
                             last_name="Degner",
                             phones=['4029813230'],
                             email="jdegner0129@gmail.com",
                             position="Software Engineer",
        )

        print 'Converting a contact to a DTO.'
        contact_dto = DTOConverter.to_dto(ContactDTO, my_contact)

        print 'Testing equality...'
        for attr, value in my_contact.__dict__.iteritems():
            self.assertEqual(getattr(my_contact, attr), getattr(contact_dto, attr),
                             "{0} attribute not equal".format(attr))

        print 'Converting a DTO to a contact.'
        my_contact = DTOConverter.from_dto(Contact, contact_dto)

        print 'Testing equality...'
        for attr, value in my_contact.__dict__.iteritems():
            self.assertEqual(getattr(my_contact, attr), getattr(contact_dto, attr),
                             "{0} attribute not equal".format(attr))

    def test_item_converter(self):
        ctx = ApplicationContext(TestableDAOContext())
        print 'Creating organization and contact item.'
        org = ctx.get_object('OrganizationDAO')
        org_dto = OrganizationDTO(name="Univerisityee of Nyeebraska-Lincoln")
        org.create_update(org_dto)
        org_model = DTOConverter.from_dto(Organization, org_dto)
        contact_item = ScrapedContact(first_name='Bee',
                                      last_name='Yee',
                                      organization={'name': "Univerisityee of Nyeebraska-Lincoln"}
        )

        print 'Converting contact to model.'
        converter = ctx.get_object('ModelConverter')
        model_contact = converter.to_model(Contact, contact_item)

        self.assertEqual(model_contact.organization.name, org_model.name)


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0]:
            raise