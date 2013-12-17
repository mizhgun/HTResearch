# Library imports
import unittest
from datetime import datetime, timedelta
from springpython.config import Object
from springpython.context import ApplicationContext

# Project imports
from HTResearch.DataModel.model import URLMetadata
from HTResearch.DataAccess.dto import URLMetadataDTO
from HTResearch.Utilities.converter import DTOConverter
from HTResearch.Utilities.context import DAOContext, URLFrontierContext
from HTResearch.Test.Mocks.connection import MockDBConnection
from HTResearch.Test.Mocks.dao import MockURLMetadataDAO


class TestableURLFrontierContext(URLFrontierContext):

    @Object()
    def RegisteredURLMetadataDAO(self):
        return MockURLMetadataDAO


class TestableDAOContext(DAOContext):

    @Object()
    def RegisteredDBConnection(self):
        return MockDBConnection


class URLFrontierTest(unittest.TestCase):
    def urlfrontier_set_up(self):
        self.frontier_ctx = ApplicationContext(TestableURLFrontierContext())
        self.dao_ctx = ApplicationContext(TestableDAOContext())

    def setUp(self):
        self.urlfrontier_tear_down()

    def tearDown(self):
        self.urlfrontier_tear_down()

    def urlfrontier_tear_down(self):
        with MockDBConnection() as db:
            db.dropall()

    def test_urlfrontier(self):
        for i in range(5):
            self.urlfrontier_set_up()
            start_time = datetime.utcnow()
            url_dao = self.dao_ctx.get_object("URLMetadataDAO")

            print 'Creating 2000 URLs'
            url_list = []
            for x in range(2000):
                url_list.append(URLMetadata(url="http://test" + str(x) + ".com",
                                            last_visited=(start_time - timedelta(days=x))))

            print 'Converting these URLs to DTOs'
            url_dtos = [DTOConverter.to_dto(URLMetadataDTO, u) for u in url_list]

            print 'Saving...'
            for dto in url_dtos:
                url_dao.create_update(dto)

            print 'Create the URLFrontier'
            frontier = self.frontier_ctx.get_object("URLFrontier")

            print 'Start the cache process'
            frontier.start_cache_process()

            print '"Create" a second frontier and verify that the frontier is a singleton'
            frontier2 = self.frontier_ctx.get_object("URLFrontier")
            self.assertEqual(frontier, frontier2)

            print 'Wait for the cache to populate and get the least recently visited URL'
            old_url = frontier.next_url()

            print 'Assert that the last visited date matches the last element in urllist'
            self.assertEqual(url_list[1999].url, old_url.url)

            print 'Push an even older URL'
            oldest_url = URLMetadata(url="http://test2001.com",
                                     last_visited=(start_time - timedelta(days=x+1)))
            frontier.put_url(oldest_url)

            print 'Empty the cache'
            frontier.empty_cache()

            print 'Wait a couple more seconds and verify that the next URL is the oldest one'
            next_url = frontier.next_url()
            self.assertEqual(oldest_url.url, next_url.url)

            print 'Stop the cache process'
            frontier.terminate_cache_process()

            self.urlfrontier_tear_down()

if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0]:
            raise