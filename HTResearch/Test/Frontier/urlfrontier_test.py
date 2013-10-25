# Library imports
import unittest
from datetime import datetime, timedelta
from time import sleep

# Project imports
from HTResearch.URLFrontier.urlfrontier import URLFrontier
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
        with URLFrontier() as frontier:
            print 'Pop the least recently visited URL'
            old_url = frontier.next_url

            print 'Assert that the last visited date matches the last element in urllist'
            self.assertEqual(old_url.last_visited, url_list[1999].last_visited)

            print 'Empty the cache'
            for x in range(1999):
                url = frontier.next_url

            print 'Wait one second and verify that the cache is being repopulated'
            sleep(1)
            self.assertFalse(frontier.empty)

if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0]:
            raise