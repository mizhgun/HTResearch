# stdlib imports
from springpython.config import *

# project imports
from HTResearch.DataAccess.dao import *
from HTResearch.URLFrontier.urlfrontier import URLFrontier


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


class DocumentScraperContext(PythonConfig):
    @Object()
    def RegisteredContactScraper(self):
        return self.ContactScraper

    @Object()
    def RegisteredOrganizationScraper(self):
        return self.OrganizationScraper

    @Object()
    def RegisteredPublicationScraper(self):
        return self.PublicationScraper


class UtilityScraperContext(PythonConfig):

    @Object()
    def RegisteredContactNameScraper(self):
        return self.ContactNameScraper

    @Object()
    def RegisteredContactPositionScraper(self):
        return self.ContactPositionScraper

    @Object()
    def RegisteredContactPublicationScraper(self):
        return self.ContactPublicationScraper

    @Object()
    def RegisteredEmailScraper(self):
        return self.EmailScraper

    @Object()
    def RegisteredKeywordScraper(self):
        return self.KeywordScraper

    @Object()
    def RegisteredIndianPhoneNumberScraper(self):
        return self.IndianPhoneNumberScraper

    @Object()
    def RegisteredOrgAddressScraper(self):
        return self.OrgAddressScraper

    @Object()
    def RegisteredOrgContactsScraper(self):
        return self.OrgContactsScraper

    @Object()
    def RegisteredOrgNameScraper(self):
        return self.OrgNameScraper

    @Object()
    def RegisteredOrgPartnersScraper(self):
        return self.OrgPartnersScraper

    @Object()
    def RegisteredOrgTypeScraper(self):
        return self.OrgTypeScraper

    @Object()
    def RegisteredOrgUrlScraper(self):
        return self.OrgUrlScraper

    @Object()
    def RegisteredPublicationAuthorsScraper(self):
        return self.PublicationAuthorsScraper

    @Object()
    def RegisteredPublicationDateScraper(self):
        return self.PublicationDateScraper

    @Object()
    def RegisteredPublicationPublisherScraper(self):
        return self.PublicationPublisherScraper

    @Object()
    def RegisteredPublicationTitleScraper(self):
        return self.PublicationTitleScraper

    @Object()
    def RegisteredPublicationTypeScraper(self):
        return self.PublicationTypeScraper

    @Object()
    def RegisteredURLMetadataScraper(self):
        return self.URLMetadataScraper


class URLFrontierContext(PythonConfig):

    @Object()
    def URLFrontier(self):
        frontier = URLFrontier()
        frontier.dao = self.RegisteredURLMetadataDAO()
        return frontier

    @Object()
    def RegisteredURLMetadataDAO(self):
        return URLMetadataDAO