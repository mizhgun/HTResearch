from dao import ContactDAO, OrganizationDAO, PublicationDAO

class DAOFactory(object):
    """A Factory class for different DAOs."""

    @staticmethod
    def GetInstance(cls):
        if cls.__name__ == "ContactDAO":
            return ContactDAO()
        elif cls.__name__ == "OrganizationDAO":
            return OrganizationDAO()
        elif cls.__name__ == "PublicationDAO":
            return PublicationDAO()