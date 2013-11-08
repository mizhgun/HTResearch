# stdlib imports
from springpython.config import *

# project imports
from HTResearch.DataAccess.dao import *
from HTResearch.URLFrontier.urlfrontier import URLFrontier
from HTResearch.WebCrawler.WebCrawler.item_pipeline.item_switches import ItemSwitch


class DAOContext(PythonConfig):

    # Contextual instances of the classes defined in this module
    @Object()
    def ContactDAO(self):
        dao = ContactDAO()
        dao.conn = self.RegisteredDBConnection()
        dao.org_dao = self.RegisteredOrganizationDAO()
        dao.pub_dao = self.RegisteredPublicationDAO()
        return dao

    @Object()
    def OrganizationDAO(self):
        dao = OrganizationDAO()
        dao.conn = self.RegisteredDBConnection()
        dao.contact_dao = self.RegisteredContactDAO()
        return dao

    @Object()
    def PublicationDAO(self):
        dao = PublicationDAO()
        dao.conn = self.RegisteredDBConnection()
        dao.contact_dao = self.RegisteredContactDAO()
        return dao

    @Object()
    def URLMetadataDAO(self):
        dao = URLMetadataDAO()
        dao.conn = self.RegisteredDBConnection()
        return dao


    # Registered classes to instantiate dependencies
    @Object()
    def RegisteredDBConnection(self):
        return DBConnection

    @Object()
    def RegisteredContactDAO(self):
        return ContactDAO

    @Object()
    def RegisteredOrganizationDAO(self):
        return OrganizationDAO

    @Object()
    def RegisteredPublicationDAO(self):
        return PublicationDAO

    @Object()
    def RegisteredURLMetadataDAO(self):
        return URLMetadataDAO


class URLFrontierContext(PythonConfig):

    @Object()
    def URLFrontier(self):
        frontier = URLFrontier()
        frontier.dao = self.RegisteredURLMetadataDAO()
        return frontier

    @Object()
    def RegisteredURLMetadataDAO(self):
        return URLMetadataDAO


class ItemPipelineContext(DAOContext, URLFrontierContext):

    @Object()
    def ItemSwitch(self):
        switch = ItemSwitch()
        switch.frontier = self.URLFrontier()
        switch.contact_dao = self.ContactDAO()
        switch.org_dao = self.OrganizationDAO()
        switch.pub_dao = self.PublicationDAO()
        switch.url_dao = self.URLMetadataDAO()
        return switch
