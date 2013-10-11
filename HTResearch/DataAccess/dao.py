from dto import *
from connection import DBConnection


class ContactDAO(object):
    """A DAO for the Contact document"""

    def create_update(self, contact_dto):
        with DBConnection():
            [OrganizationDAO().create_update(o) for o in contact_dto.organizations]
            [PublicationDAO().create_update(p) for p in contact_dto.publications]

            contact_dto.save()

    def delete(self, contact_dto):
        with DBConnection():
            contact_dto.delete()

    # NOTE: This method will not return an object when
    # passed constraints that are reference types!
    def find(self, **constraints):
        with DBConnection():
            return ContactDTO.objects(**constraints).first()

    # NOTE: This method will not return an object when
    # passed constraints that are reference types!
    def findmany(self, num_elements, *sort_fields, **constraints):
        with DBConnection():
            if len(sort_fields) > 0:
                return ContactDTO.objects(**constraints).order_by(*sort_fields)[:num_elements]
            else:
                return ContactDTO.objects(**constraints)[:num_elements]


class OrganizationDAO(object):
    """A DAO for the Organization document"""

    def create_update(self, org_dto):
        with DBConnection():
            [ContactDAO().create_update(c) for c in org_dto.contacts]

            org_dto.save()

    def delete(self, org_dto):
        with DBConnection():
            org_dto.delete()

    # NOTE: This method will not return an object when
    # passed constraints that are reference types!
    def find(self, **constraints):
        with DBConnection():
            return OrganizationDTO.objects(**constraints).first()

    # NOTE: This method will not return an object when
    # passed constraints that are reference types!
    def findmany(self, num_elements, *sort_fields, **constraints):
        with DBConnection():
            if len(sort_fields) > 0:
                return OrganizationDTO.objects(**constraints).order_by(*sort_fields)[:num_elements]
            else:
                return OrganizationDTO.objects(**constraints)[:num_elements]


class PublicationDAO(object):
    """A DAO for the Publication document"""

    def create_update(self, pub_dto):
        with DBConnection():
            [ContactDAO().create_update(c) for c in pub_dto.authors]

            if pub_dto.publisher is not None:
                ContactDAO().create_update(pub_dto.publisher)

            pub_dto.save()

    def delete(self, pub_dto):
        with DBConnection():
            pub_dto.delete()

    # NOTE: This method will not return an object when
    # passed constraints that are reference types!
    def find(self, **constraints):
        with DBConnection():
            return PublicationDTO.objects(**constraints).first()

    # NOTE: This method will not return an object when
    # passed constraints that are reference types!
    def findmany(self, num_elements, *sort_fields, **constraints):
        with DBConnection():
            if len(sort_fields) > 0:
                return PublicationDTO.objects(**constraints).order_by(*sort_fields)[:num_elements]
            else:
                return PublicationDTO.objects(**constraints)[:num_elements]


class URLMetadataDAO(object):
    """A DAO for the URLMetadata document"""

    def create_update(self, url_dto):
        with DBConnection():
            url_dto.save(cascade=True)

    def delete(self, url_dto):
        with DBConnection():
            url_dto.delete()

    # NOTE: This method will not return an object when
    # passed constraints that are reference types!
    def find(self, **constraints):
        with DBConnection():
            return URLMetadataDTO.objects(**constraints).first()

    # NOTE: This method will not return an object when
    # passed constraints that are reference types!
    def findmany(self, num_elements, *sort_fields, **constraints):
        with DBConnection():
            if len(sort_fields) > 0:
                return URLMetadataDTO.objects(**constraints).order_by(*sort_fields)[:num_elements]
            else:
                return URLMetadataDTO.objects(**constraints)[:num_elements]