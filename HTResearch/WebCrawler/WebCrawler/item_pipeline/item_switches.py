import sys

[sys.path.remove(p) for p in sys.path if 'DataModel' in p]
[sys.path.remove(p) for p in sys.path if 'DataAccess' in p]
sys.path.append('../DataModel/')
sys.path.append('../DataAccess/')

from scrapy.exceptions import DropItem
from dao import *
from dto import *
from factory import *
from converter import *
from WebCrawler.converter import ModelConverter 

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

    def _store_contact(self, scraped_contact):
        # item to model
        contact = ModelConverter.to_model(Contact, scraped_contact)
        # model to dto...
        contact_dto = DTOConverter.to_dto(ContactDTO, contact)
        # get dao
        dao = DAOFactory.get_instance(ContactDAO)
        #store
        dao.create_update(contact_dto)

    def _store_organization(self, scraped_org):
        # item to model
        org = ModelConverter.to_model(Organization, scraped_org)
        # model to dto...
        org_dto = DTOConverter.to_dto(OrganizationDTO, org)
        # get dao
        dao = DAOFactory.get_instance(OrganizationDAO)
        #store
        dao.create_update(org_dto)

    def _store_publication(self, scraped_pub):
        # item to model
        pub = ModelConverter.to_model(Publication, scraped_pub)
        # model to dto...
        pub_dto = DTOConverter.to_dto(PublicationDTO, pub)
        # get dao
        dao = DAOFactory.get_instance(PublicationDAO)
        #store
        dao.create_update(pub_dto)

