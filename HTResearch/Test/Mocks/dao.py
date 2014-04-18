from HTResearch.DataAccess.dto import *
from connection import MockDBConnection


class MockDAO(object):
    """
    A generic DAO class that may be subclassed by DAOs for operations on
    specific documents.
    """

    def __init__(self):
        self.conn = MockDBConnection

        # Implemented in children
        self.dto = None

    def merge_documents(self, dto, merge_dto):
        return dto

    def create_update(self, dto):
        pass

    def delete(self, dto):
        pass

    # NOTE: This method will not return an object when
    # passed constraints that are reference types!
    def find(self, **constraints):
        with self.conn():
            return self.dto.objects(**constraints).first()

    # NOTE: This method will not return an object when
    # passed constraints that are reference types!
    def findmany(self, num_elements=None, page_size=None, page=None, start=None, end=None, sort_fields=[],
                 **constraints):
        with self.conn():
            if len(sort_fields) > 0:
                ret = self.dto.objects(**constraints).order_by(*sort_fields)
            else:
                ret = self.dto.objects(**constraints)
            if num_elements is not None:
                return ret[:num_elements]
            elif page_size is not None and page is not None:
                # as an example, if we want page 3 with a page size of 50, we want elements with index 150 to 199
                pg_start = page_size * page
                pg_end = page_size * (page + 1)
                # NOTE: Even though end would equal 200 in our example, python's slicing is not inclusive for end
                return ret[pg_start:pg_end]
            elif start is not None:
                if end is None:
                    return ret[start:]
                else:
                    return ret[start:end + 1]

            return ret


class MockContactDAO(MockDAO):
    """
    A DAO for the Contact document
    """

    def __init__(self):
        super(MockContactDAO, self).__init__()
        self.dto = ContactDTO
        self.org_dao = MockOrganizationDAO
        self.pub_dao = MockPublicationDAO

    def create_update(self, contact_dto, cascade_add=True):
        no_id = contact_dto.id is None
        with self.conn():
            if cascade_add:
                o = contact_dto.organization
                if o:
                    if contact_dto in o.contacts and no_id:
                        o.contacts.remove(contact_dto)
                    contact_dto.organization = self.org_dao().create_update(o, False)
                for i in range(len(contact_dto.publications)):
                    p = contact_dto.publications[i]
                    if contact_dto in p.authors and no_id:
                        p.authors.remove(contact_dto)
                    contact_dto.publications[i] = self.pub_dao().create_update(p, False)

            contact_dto.save()

        return contact_dto

class MockOrganizationDAO(MockDAO):
    """
    A DAO for the Organization document
    """

    def __init__(self):
        super(MockOrganizationDAO, self).__init__()
        self.dto = OrganizationDTO
        self.contact_dao = MockContactDAO
        self.geocode = lambda x: [0, 0]

    def create_update(self, org_dto, cascade_add=True):
        with self.conn():
            if cascade_add:
                for i in range(len(org_dto.contacts)):
                    c = org_dto.contacts[i]
                    if c.organization is not None and c.organization == org_dto:
                        c.organization = None
                    org_dto.contacts[i] = self.contact_dao().create_update(c, False)

                for i in range(len(org_dto.partners)):
                    p = org_dto.partners[i]
                    if org_dto in p.partners:
                        p.partners.remove(org_dto)
                    org_dto.partners[i] = self.create_update(p, False)

            org_dto.save()
        return org_dto


class MockPublicationDAO(MockDAO):
    """
    A DAO for the Publication document
    """

    def __init__(self):
        super(MockPublicationDAO, self).__init__()
        self.dto = PublicationDTO
        self.contact_dao = MockContactDAO

    def create_update(self, pub_dto, cascade_add=True):
        no_id = pub_dto.id is None
        with self.conn():
            if cascade_add:
                for i in range(len(pub_dto.authors)):
                    c = pub_dto.authors[i]
                    if pub_dto in c.publications and no_id:
                        c.publications.remove(pub_dto)
                    pub_dto.authors[i] = self.contact_dao().create_update(c, False)

                if pub_dto.publisher is not None:
                    if pub_dto in pub_dto.publisher.publications and no_id:
                        pub_dto.publisher.publications.remove(pub_dto)
                    pub_dto.publisher = self.contact_dao().create_update(pub_dto.publisher, False)

            pub_dto.save()
        return pub_dto

class MockURLMetadataDAO(MockDAO):
    """
    A DAO for the URLMetadata document
    """

    def __init__(self):
        super(MockURLMetadataDAO, self).__init__()
        self.dto = URLMetadataDTO

    def create_update(self, url_dto):
        with self.conn():
            url_dto.save()
        return url_dto


class MockUserDAO(MockDAO):
    def __init__(self):
        super(MockUserDAO, self).__init__()
        self.dto = UserDTO

        # Injected dependencies
        self.org_dao = MockOrganizationDAO

    def create_update(self, user_dto):
        with self.conn():
            if user_dto.organization is not None:
                o = user_dto.organization
                user_dto.organization = self.org_dao().create_update(o)

            user_dto.save()
        return user_dto
