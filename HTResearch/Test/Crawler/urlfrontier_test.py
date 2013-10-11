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
        urllist = []
        [urllist.append(URLMetadata(url="http://test.com",
                                    last_visited=(start_time - timedelta(days=x))))
         for x in range(2000)]

        # To DTOs
        url_dtos = [DTOConverter.to_dto(URLMetadataDTO, u) for u in urllist]

        # Save to the daterbase
        [url_dao.create_update(dto) for dto in url_dtos]

        # Create the URLFrontier
        frontier = URLFrontier()

        # Pop the least recently visited URL
        old_url = frontier.pop_url()

        # Assert that the size of the URL queue is 1000
        self.assertEquals(old_url.last_visited, urllist[1999].last_visited)