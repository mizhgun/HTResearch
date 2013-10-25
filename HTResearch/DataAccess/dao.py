from dto import *
from connection import DBConnection


class DAO(object):
    """
    A generic DAO class that may be subclassed by DAOs for operations on
    specific documents.
    """

    @staticmethod
    def merge_documents(dto, merge_dto):
        with DBConnection():
            attributes = merge_dto._data
            for key in attributes:
                if attributes[key] is not None:
                    cur_attr = getattr(dto, key)
                    if cur_attr is None:
                        setattr(dto, key, attributes[key])
                    else:
                        # TODO: Maybe we should merge all reference documents, as well?
                        pass
            dto.save()


class ContactDAO(DAO):
    """
    A DAO for the Contact document
    """

    def create_update(self, contact_dto):
        with DBConnection():
            [OrganizationDAO().create_update(o) for o in contact_dto.organizations]
            [PublicationDAO().create_update(p) for p in contact_dto.publications]

            if contact_dto.id is None:
                existing_dto = ContactDTO.objects(email=contact_dto.email).first()
                if existing_dto is not None:
                    self.merge_documents(existing_dto, contact_dto)
                    return

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


class OrganizationDAO(DAO):
    """
    A DAO for the Organization document
    """

    def create_update(self, org_dto):
        with DBConnection():
            [ContactDAO().create_update(c) for c in org_dto.contacts]

            if org_dto.id is None:
                existing_dto = OrganizationDTO.objects(email=org_dto.email).first()
                if existing_dto is not None:
                    self.merge_documents(existing_dto, org_dto)
                    return

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


class PublicationDAO(DAO):
    """
    A DAO for the Publication document
    """

    def create_update(self, pub_dto):
        with DBConnection():
            [ContactDAO().create_update(c) for c in pub_dto.authors]

            if pub_dto.id is None:
                existing_dto = PublicationDTO.objects(title=pub_dto.title).first()
                if existing_dto is not None:
                    self.merge_documents(existing_dto, pub_dto)
                    return

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


class URLMetadataDAO(DAO):
    """
    A DAO for the URLMetadata document
    """

    def create_update(self, url_dto):
        with DBConnection():
            if url_dto.id is None:
                existing_dto = URLMetadataDTO.objects(url=url_dto.url).first()
                if existing_dto is not None:
                    self.merge_documents(existing_dto, url_dto)
                    return

            url_dto.save()

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