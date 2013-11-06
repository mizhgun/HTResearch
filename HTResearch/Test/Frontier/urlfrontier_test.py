# Library imports
import unittest
from datetime import datetime, timedelta
from time import sleep

# Project imports
from HTResearch.URLFrontier.urlfrontier import URLFrontier, URLFrontierRules
from HTResearch.DataAccess.connection import DBConnection
from HTResearch.DataModel.model import URLMetadata
from HTResearch.DataAccess.factory import DAOFactory
from HTResearch.DataAccess.dao import URLMetadataDAO
from HTResearch.DataAccess.dto import URLMetadataDTO
from HTResearch.DataModel.converter import DTOConverter


class URLFrontierTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        with DBConnection() as c:
            c.dropall()

    def test_urlfrontier(self):
        start_time = datetime.now()
        url_dao = DAOFactory.get_instance(URLMetadataDAO)
        rules = URLFrontierRules()

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
        frontier = URLFrontier()

        print 'Start the cache process'
        frontier.start_cache_process()

        print '"Create" a second frontier and verify that the frontier is a singleton'
        frontier2 = URLFrontier()
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

if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0]:
            raise