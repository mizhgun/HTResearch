from scrapy.exceptions import DropItem

from HTResearch.DataAccess.dao import *
from HTResearch.Utilities.converter import *
from HTResearch.URLFrontier.urlfrontier import URLFrontier
from HTResearch.Utilities.logutil import LoggingSection, LoggingUtility
from HTResearch.WebCrawler.WebCrawler.items import ScrapedContact, ScrapedOrganization, ScrapedPublication, ScrapedUrl


logger = LoggingUtility().get_logger(LoggingSection.CRAWLER, __name__)


class ItemSwitch(object):
    """Redirect Items to Appropriate Pipeline Handler"""

    def __init__(self):
        self.frontier = URLFrontier()
        self.contact_dao = ContactDAO()
        self.org_dao = OrganizationDAO()
        self.pub_dao = PublicationDAO()
        self.url_dao = URLMetadataDAO()

    def process_item(self, item, spider):
        """Consumes item from spider and passes to correct handler asynchronously"""

        # switch to handle item based on class type
        if isinstance(item, ScrapedUrl):
            # Create DAO for URL with empty fields
            # Pass it to URLFrontier, which will add it iff it is new
            self._store_url(item)
            pass 
        elif isinstance(item, ScrapedContact):
            self._store_contact(item)
        elif isinstance(item, ScrapedOrganization):
            self._store_organization(item)
        elif isinstance(item, ScrapedPublication):
            self._store_publication(item)
        else:
            msg = "No behavior defined for item of type %s" % item.__class__.__name__
            logger.error(msg)
            raise DropItem(msg)
        
        # return item to next piece of pipeline
        return item

    def _store_contact(self, scraped_contact):
        # item to Model
        contact = ModelConverter.to_model(Contact, scraped_contact)
        # Model to dto...
        contact_dto = DTOConverter.to_dto(ContactDTO, contact)
        # get dao
        dao = self.contact_dao
        #store
        dao.create_update(contact_dto)

    def _store_organization(self, scraped_org):
        # item to Model
        org = ModelConverter.to_model(Organization, scraped_org)
        # Model to dto...
        org_dto = DTOConverter.to_dto(OrganizationDTO, org)
        # get dao
        dao = self.org_dao
        #store
        dao.create_update(org_dto)

    def _store_publication(self, scraped_pub):
        # item to Model
        pub = ModelConverter.to_model(Publication, scraped_pub)
        # Model to dto...
        pub_dto = DTOConverter.to_dto(PublicationDTO, pub)
        # get dao
        dao = self.pub_dao
        #store
        dao.create_update(pub_dto)

    def _store_url(self, scraped_url):
        # For now, store the new metadata ourselves
        # item to Model
        url = ModelConverter.to_model(URLMetadata, scraped_url)

        frontier = self.frontier
        frontier.put_url(url)
