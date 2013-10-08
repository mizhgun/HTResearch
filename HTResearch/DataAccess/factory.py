from dao import *


class DAOFactory(object):
    """A Factory class for different DAOs."""

    @staticmethod
    def get_instance(cls):
        if cls.__name__ == "ContactDAO":
            return ContactDAO()
        elif cls.__name__ == "OrganizationDAO":
            return OrganizationDAO()
        elif cls.__name__ == "PublicationDAO":
            return PublicationDAO()
        elif cls.__name__ == "URLMetadataDAO":
            return URLMetadataDAO()