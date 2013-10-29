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
            return dto


class ContactDAO(DAO):
    """
    A DAO for the Contact document
    """

    def create_update(self, contact_dto):
        with DBConnection():
            for i in range(len(contact_dto.organizations)):
                o = contact_dto.organizations[i]
                contact_dto.organizations[i] = OrganizationDAO().create_update(o)
            for i in range(len(contact_dto.publications)):
                p = contact_dto.publications[i]
                contact_dto.publications[i] = PublicationDAO().create_update(p)

            if contact_dto.id is None:
                existing_dto = ContactDTO.objects(email=contact_dto.email).first()
                if existing_dto is not None:
                    saved_dto = self.merge_documents(existing_dto, contact_dto)
                    return saved_dto

            contact_dto.save()
        return contact_dto

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
            for i in range(len(org_dto.contacts)):
                c = org_dto.contacts[i]
                org_dto.contacts[i] = ContactDAO().create_update(c)

            if org_dto.id is None:
                existing_dto = OrganizationDTO.objects(email_key__in=org_dto.emails).first()
                if existing_dto is not None:
                    saved_dto = self.merge_documents(existing_dto, org_dto)
                    return saved_dto

            org_dto.save()
        return org_dto

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
            for i in range(len(pub_dto.authors)):
                c = pub_dto.authors[i]
                pub_dto.authors[i] = ContactDAO().create_update(c)

            if pub_dto.id is None:
                existing_dto = PublicationDTO.objects(title=pub_dto.title).first()
                if existing_dto is not None:
                    saved_dto = self.merge_documents(existing_dto, pub_dto)
                    return saved_dto

            if pub_dto.publisher is not None:
                ContactDAO().create_update(pub_dto.publisher)

            pub_dto.save()
        return pub_dto

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
                    saved_dto = self.merge_documents(existing_dto, url_dto)
                    return saved_dto

            url_dto.save()
        return url_dto

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