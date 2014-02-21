#stdlib imports
import os
import pickle
import unittest
from springpython.context import ApplicationContext
from springpython.config import Object

# project imports
from HTResearch.DataModel.model import Organization
from HTResearch.PageRank.algorithms import *
from HTResearch.Test.Mocks.dao import *
from HTResearch.Utilities.context import PageRankContext
from HTResearch.Utilities.converter import DTOConverter

RESOURCES_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')


class TestableDAOContext(PageRankContext):
    @Object()
    def RegisteredDBConnection(self):
        return MockDBConnection


class PageRankTest(unittest.TestCase):
    def setUp(self):
        with MockDBConnection() as db:
            db.dropall()

        self.ctx = ApplicationContext(TestableDAOContext())

        with open(os.path.join(RESOURCES_DIRECTORY, 'organizations'), mode='r') as to_read:
            org_models = pickle.load(to_read)

        # freeze these out b/c we didn't store them
        for model in org_models:
            del model.contacts

        org_dtos = [DTOConverter.to_dto(OrganizationDTO, o) for o in org_models]

        org_dao = self.ctx.get_object('OrganizationDAO')
        for dto in org_dtos:
            org_dao.create_update(dto)

        with open(os.path.join(RESOURCES_DIRECTORY, 'ranked_organizations'), mode='r') as to_read:
            self.assert_models = pickle.load(to_read)


    def tearDown(self):
        with MockDBConnection() as db:
            db.dropall()

    def test_page_rank(self):
        print 'Creating PageRankPreprocessor'
        prp = self.ctx.get_object('PageRankPreprocessor')

        print 'Bring organizations to memory'
        orgs = prp.bring_orgs_to_memory()

        print 'Cleaning organizations'
        orgs = prp.cleanup_data(orgs)

        print 'Creating dat matrix'
        matrix = prp.create_matrix(orgs)
        self.assertIsNotNone(matrix)

        print 'Creating the dampened google matrix'
        matrix = google_matrix(matrix)

        print 'Generating eigenvector'
        vector = left_eigenvector(matrix)

        print 'Creating PageRankPostprocessor'
        post = self.ctx.get_object('PageRankPostprocessor')

        print 'Assigning ranks to organizations'
        orgs = post.give_orgs_ranks(orgs, vector)

        print 'Storing organizations'
        post.store_organizations(orgs)

        dao = self.ctx.get_object('OrganizationDAO')
        new_org_models = [DTOConverter.from_dto(Organization, o) for o in dao.all()]

        self.assertEqual(len(new_org_models), len(self.assert_models),
                         "Error: returned model number different than expected")

        for model in self.assert_models:
            self._compare_assert_against_test(model, new_org_models)

    def _compare_assert_against_test(self, model, models):
        new_model = None
        for i in range(0, len(models)):
            if models[i].name == model.name:
                new_model = models[i]

        self.assertIsNotNone(new_model, "Error: did not find a model by name %s" % model.name)

        self.assertEqual(model.page_rank, new_model.page_rank, "Different ranks!")
        self.assertEqual(model.page_rank_weight, new_model.page_rank_weight, "Different rank weights!")


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0]:
            raise
