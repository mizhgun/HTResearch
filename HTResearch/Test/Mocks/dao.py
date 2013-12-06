from mongoengine import Q
from HTResearch.DataAccess.dto import *
from connection import MockDBConnection
from HTResearch.DataModel.enums import OrgTypesEnum


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
        with self.conn():
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

    def create_update(self, dto):
        pass

    def delete(self, dto):
        with self.conn():
            dto.delete()

    # NOTE: This method will not return an object when
    # passed constraints that are reference types!
    def find(self, **constraints):
        with self.conn():
            return self.dto.objects(**constraints).first()

    # NOTE: This method will not return an object when
    # passed constraints that are reference types!
    def findmany(self, num_elements=None, page_size=None, page=None, start=None, end=None, sort_fields=[], **constraints):
        with self.conn():
            if len(sort_fields) > 0:
                ret = self.dto.objects(**constraints).order_by(sort_fields)
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
                    return ret[start:end+1]

            return ret

    def findmany_by_domains(self, num_elements, required_domains, blocked_domains, *sort_fields):
        if len(required_domains) > 0:
            req_query = Q(domain__in=required_domains)
        else:
            req_query = Q()
        if len(blocked_domains) > 0:
            blk_query = Q(domain__nin=blocked_domains)
        else:
            blk_query = Q()

        with self.conn():
            if len(sort_fields) > 0:
                return URLMetadataDTO.objects(req_query & blk_query).order_by(*sort_fields)[:num_elements]
            else:
                return URLMetadataDTO.objects(req_query & blk_query)[:num_elements]

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
        with self.conn():
            o = contact_dto.organization
            if o:
                if contact_dto not in o.contacts:
                    o.contacts.append(contact_dto)
                contact_dto.organization = self.org_dao().create_update(o, False)
            for i in range(len(contact_dto.publications)):
                p = contact_dto.publications[i]
                contact_dto.publications[i] = self.pub_dao().create_update(p, False)

            if contact_dto.id is None:
                existing_dto = self.dto.objects(email=contact_dto.email).first()
                if existing_dto is not None:
                    saved_dto = self.merge_documents(existing_dto, contact_dto)
                    return saved_dto
            if cascade_add:
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

    def merge_documents(self, existing_org_dto, new_org_dto, cascade_add=True):
            with self.conn():
                attributes = new_org_dto._data
                for key in attributes:
                    if attributes[key]:
                        cur_attr = getattr(existing_org_dto, key)
                        if not cur_attr:
                            setattr(existing_org_dto, key, attributes[key])
                        elif type(cur_attr) is list:
                            merged_list = list(set(cur_attr + attributes[key]))
                            # if this is org types and we have more than one org type, make sure unknown isn't a type :P
                            if key == "types" and len(merged_list) > 1 and OrgTypesEnum.UNKNOWN in merged_list:
                                merged_list.remove(OrgTypesEnum.UNKNOWN)
                            setattr(existing_org_dto, key, attributes[key])
                if cascade_add:
                    existing_org_dto.save()
                return existing_org_dto

    def create_update(self, org_dto, cascade_add=True):
        with self.conn():
            if cascade_add:
                for i in range(len(org_dto.contacts)):
                    c = org_dto.contacts[i]
                    org_dto.contacts[i] = self.contact_dao().create_update(c, False)

            if org_dto.id is None:
                existing_dto = self._smart_search_orgs(org_dto)
                if existing_dto is not None:
                    saved_dto = self.merge_documents(existing_dto, org_dto, False)
                    return saved_dto
            if cascade_add:
                org_dto.save()
        return org_dto

    def _smart_search_orgs(self, org_dto):
        # organizations have unique phone numbers
        if org_dto.phone_numbers:
            same_phone = Q(phone_numbers__in=org_dto.phone_numbers)
        else:
            same_phone = Q()

        # organizations have unique emails
        if org_dto.emails:
            same_email = Q(emails__in=org_dto.emails)
        else:
            same_email = Q()

        # organizations have unique URLs
        if org_dto.organization_url:
            same_url = Q(organization_url=org_dto.organization_url)
        else:
            same_url = Q()

        # organizations have unique Facebooks
        if org_dto.facebook:
            same_fb = Q(facebook=org_dto.facebook)
        else:
            same_fb = Q()

        # organizations have unique Twitters
        if org_dto.twitter:
            same_twitter = Q(twitter=org_dto.twitter)
        else:
            same_twitter = Q()

        existing_dto = self.dto.objects(same_phone | same_email | same_url | same_fb | same_twitter).first()
        return existing_dto


class MockPublicationDAO(MockDAO):
    """
    A DAO for the Publication document
    """
    def __init__(self):
        super(MockPublicationDAO, self).__init__()
        self.dto = PublicationDTO
        self.contact_dao = MockContactDAO

    def create_update(self, pub_dto, cascade_add=True):
        with self.conn():
            for i in range(len(pub_dto.authors)):
                c = pub_dto.authors[i]
                pub_dto.authors[i] = self.contact_dao().create_update(c, False)

            if pub_dto.id is None:
                existing_dto = self.dto.objects(title=pub_dto.title).first()
                if existing_dto is not None:
                    saved_dto = self.merge_documents(existing_dto, pub_dto)
                    return saved_dto

            if pub_dto.publisher is not None:
                self.contact_dao().create_update(pub_dto.publisher)
            if cascade_add:
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
            if url_dto.id is None:
                existing_dto = self.dto.objects(url=url_dto.url).first()
                if existing_dto is not None:
                    saved_dto = self.merge_documents(existing_dto, url_dto)
                    return saved_dto

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
