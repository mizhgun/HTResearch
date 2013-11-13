# stdlib imports
from springpython.config import *

# project imports
from HTResearch.DataAccess.dao import *
from HTResearch.URLFrontier.urlfrontier import URLFrontier
from HTResearch.WebCrawler.WebCrawler.scrapers.document_scrapers import *
from HTResearch.WebCrawler.WebCrawler.scrapers.utility_scrapers import UrlMetadataScraper


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
    def ContactScraper(self):
        return ContactScraper()

    @Object()
    def OrganizationScraper(self):
        org = OrganizationScraper()
        org._scrapers = {
            'name': [self.RegisteredOrgNameScraper()],
            'address': [self.RegisteredOrgAddressScraper()],
            'types': [self.RegisteredOrgTypeScraper()],
            'phone_number': [self.RegisteredUSPhoneNumberScraper(), self.RegisteredIndianPhoneNumberScraper()],
            'email': [self.RegisteredEmailScraper()],
            'contacts': [self.RegisteredOrgContactsScraper()],
            'organization_url': [self.RegisteredOrgUrlScraper()],
            'partners': [self.RegisteredOrgPartnersScraper()],
        }
        return org

    @Object()
    def PublicationScraper(self):
        return PublicationScraper()

    # Registered classes
    @Object()
    def RegisteredEmailScraper(self):
        return EmailScraper

    @Object()
    def RegisteredKeywordScraper(self):
        return KeywordScraper

    @Object()
    def RegisteredIndianPhoneNumberScraper(self):
        return IndianPhoneNumberScraper

    @Object()
    def RegisteredOrgAddressScraper(self):
        return OrgAddressScraper

    @Object()
    def RegisteredOrgContactsScraper(self):
        return OrgContactsScraper

    @Object()
    def RegisteredOrgNameScraper(self):
        return OrgNameScraper

    @Object()
    def RegisteredOrgPartnersScraper(self):
        return OrgPartnersScraper

    @Object()
    def RegisteredOrgTypeScraper(self):
        return OrgTypeScraper

    @Object()
    def RegisteredOrgUrlScraper(self):
        return OrgUrlScraper

    @Object()
    def RegisteredUSPhoneNumberScraper(self):
        return USPhoneNumberScraper


class UrlMetadataScraperContext(PythonConfig):

    @Object()
    def UrlMetadataScraper(self):
        scraper = UrlMetadataScraper()
        scraper.dao = self.RegisteredURLMetadataDAO()
        return scraper

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