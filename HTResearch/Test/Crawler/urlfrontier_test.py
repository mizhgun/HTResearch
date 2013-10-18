# Library imports
import unittest
from datetime import datetime, timedelta

# Project imports
from HTResearch.WebCrawler.WebCrawler.urlfrontier.urlfrontier import URLFrontier
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

        # Store URLs with an increasing timedelta from the start time of the test
        url_list = []
        for x in range(2000):
            url_list.append(URLMetadata(url="http://test.com",
                                        last_visited=(start_time - timedelta(days=x))))

        # To DTOs
        url_dtos = [DTOConverter.to_dto(URLMetadataDTO, u) for u in url_list]

        # Save to the database
        for dto in url_dtos:
            url_dao.create_update(dto)

        # Create the URLFrontier
        frontier = URLFrontier()

        # Pop the least recently visited URL
        old_url = frontier.next_url

        # Assert that the last visited date matches the last element in urllist
        # and that the size of the queue is 999
        self.assertEqual(old_url.last_visited, url_list[1999].last_visited)
        self.assertEqual(frontier.size, 999)

        # Push a new URL to the queue
        frontier.put_url("http://test2.com")

        # Assert that the queue is now full
        self.assertTrue(frontier.urls.full())

        # Pop every URL
        for i in range(1000):
            next_url = frontier.next_url

        # Make sure the URL we just pushed is what we get last and
        # that the queue is empty

        self.assertEqual(next_url, "http://test2.com")
        self.assertTrue(frontier.urls.empty())