# stdlib imports
from springpython.config import *

# project imports
from HTResearch.DataAccess.dao import *
from HTResearch.URLFrontier.urlfrontier import URLFrontier


class DAOContext(PythonConfig):

    @Object()
    def ContactDAO(self):
        dao = ContactDAO()
        dao.conn = self.DBConnection()
        return dao

    @Object()
    def OrganizationDAO(self):
        dao = OrganizationDAO()
        dao.conn = self.DBConnection()
        return dao

    @Object()
    def PublicationDAO(self):
        dao = PublicationDAO()
        dao.conn = self.DBConnection()
        return dao

    @Object()
    def URLMetadataDAO(self):
        dao = URLMetadataDAO()
        dao.conn = self.DBConnection()
        return dao

    @Object()
    def DBConnection(self):
        return DBConnection


class URLFrontierContext(PythonConfig):

    @Object()
    def URLFrontier(self):
        frontier = URLFrontier()
        frontier.dao = self.URLMetadataDAO()

    @Object()
    def URLMetadataDAO(self):
        return URLMetadataDAO()