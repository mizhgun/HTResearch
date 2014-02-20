#stdlib imports
import unittest
from springpython.context import ApplicationContext
from springpython.config import Object

# project imports
from HTResearch.PageRank.algorithms import *
from HTResearch.Test.Mocks.dao import *
from HTResearch.Utilities.context import PageRankContext


class TestableDAOContext(PageRankContext):
    @Object()
    def RegisteredDBConnection(self):
        return MockDBConnection


class PageRankTest(unittest.TestCase):
    def test_preprocessor(self):
        ctx = ApplicationContext(TestableDAOContext())
        print 'Creating PageRankPreprocessor'
        prp = ctx.get_object('PageRankPreprocessor')
        orgs = prp.bring_orgs_to_memory()
        orgs = prp.cleanup_data(orgs)
        matrix = prp.create_matrix(orgs)
        matrix = google_matrix(matrix)
        vector = left_eigenvector(matrix)
        post = ctx.get_object('PageRankPostprocessor')
        orgs = post.give_orgs_ranks(orgs, vector)
        post.store_organizations(orgs)
        pass


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0]:
            raise
