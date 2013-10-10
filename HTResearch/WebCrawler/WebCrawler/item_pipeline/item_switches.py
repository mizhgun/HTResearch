from scrapy.exceptions import DropItem
from HTResearch.DataAccess.dao import *
from HTResearch.DataAccess.factory import *
from HTResearch.DataModel.converter import *


class ItemSwitch(object):
    """Redirect Items to Appropriate Pipeline Handler"""

    def __init__(self):
        pass

    def process_item(self, item, spider):
        """Consumes item from spider and passes to correct handler asynchronously"""

        # extract the class of the item
        item_class = item.__class__.__name__

        # switch to handle item based on class type
        if item_class == "ScrapedUrl":
            # Create DAO for URL with empty fields
            # Pass it to URLFrontier, which will add it iff it is new 
            pass 
        elif item_class == "ScrapedContact":
            self._store_contact(item)
        elif item_class == "ScrapedOrganization":
            self._store_organization(item)
        elif item_class == "ScrapedPublication":
            self._store_publication(item)
        else:
            raise DropItem("No behavior defined for item of type %s" % item_class)
        
        # return item to next piece of pipeline
        return item

    @staticmethod
    def _store_contact(scraped_contact):
        # item to Model
        contact = ModelConverter.to_model(Contact, scraped_contact)
        # Model to dto...
        contact_dto = DTOConverter.to_dto(ContactDTO, contact)
        # get dao
        dao = DAOFactory.get_instance(ContactDAO)
        #store
        dao.create_update(contact_dto)

    @staticmethod
    def _store_organization(scraped_org):
        # item to Model
        org = ModelConverter.to_model(Organization, scraped_org)
        # Model to dto...
        org_dto = DTOConverter.to_dto(OrganizationDTO, org)
        # get dao
        dao = DAOFactory.get_instance(OrganizationDAO)
        #store
        dao.create_update(org_dto)

    @staticmethod
    def _store_publication(scraped_pub):
        # item to Model
        pub = ModelConverter.to_model(Publication, scraped_pub)
        # Model to dto...
        pub_dto = DTOConverter.to_dto(PublicationDTO, pub)
        # get dao
        dao = DAOFactory.get_instance(PublicationDAO)
        #store
        dao.create_update(pub_dto)

