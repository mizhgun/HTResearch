#
# dao.py
# A module containing the different data access objects used for interaction with our MongoDB collections.
#


from datetime import datetime
from mongoengine import Q
from mongoengine.fields import StringField

from dto import *

from connection import DBConnection
from HTResearch.DataModel.enums import OrgTypesEnum
from HTResearch.Utilities.geocoder import geocode
from HTResearch.Utilities.url_tools import UrlUtility
import re


class DAO(object):
    """
    A generic DAO class that may be subclassed by DAOs for operations on
    specific documents.

    Attributes:
        conn (DBConnection): The database connection class to use.
    """

    def __init__(self):
        self.conn = DBConnection

    def all(self, *only):
        """
        Returns all documents in the collection.

        Arguments:
            only (param[]): The specific fields to return from the collection, if any.

        Returns:
            The documents or specified fields in the collection.
        """
        with self.conn():
            return self.dto.objects(self._valid_query()).only(*only)

    def merge_documents(self, dto, merge_dto):
        """
        Merges two documents (the latter document into the former).

        Arguments:
            dto (DTO): The base DTO to merge into.
            merge_dto (DTO): The DTO with information to be merged.

        Returns:
            The newly merged DTO.
        """
        with self.conn():
            attributes = merge_dto._data
            for key in attributes:
                if attributes[key] is not None:
                    cur_attr = getattr(dto, key)
                    if cur_attr is None or (isinstance(cur_attr, type([])) and len(cur_attr) == 0):
                        setattr(dto, key, attributes[key])
                    else:
                        # TODO: Maybe we should merge all reference documents, as well?
                        pass

            dto.last_updated = datetime.utcnow()
            dto.save()
            return dto

    def create_update(self, dto):
        """
        Creates or updates a document.

        Arguments:
            dto (DTO): The DTO to be created or updated.

        Returns:
            The newly created or updated DTO.
        """
        pass

    def delete(self, dto):
        """
        Deletes an existing document.

        Arguments:
            dto (DTO): The DTO to be deleted.
        """
        with self.conn():
            dto.delete()

    # NOTE: This method will not return an object when
    # passed constraints that are reference types!
    def find(self, **constraints):
        """
        Finds and returns a single (valid) document.

        Arguments:
            constraints (param[]): The constraints to apply to the find operation.

        Returns:
            A DTO matching the constraints provided.
        """
        with self.conn():
            return self.dto.objects(Q(**constraints) & self._valid_query()).first()

    def count(self, search=None, **constraints):
        """
        Returns the number of documents that satisfy a query.

        Arguments:
            search (string): A text search to apply to documents' fields.
            constraints (param[]): The constraints to apply to the count operation.

        Returns:
            The number of documents matching the constraints provided.
        """
        with self.conn():
            # Do text search or grab by constraints
            if search is not None:
                return len(self._text_search(search, None))
            else:
                return self.dto.objects(Q(**constraints) & self._valid_query()).count()

    # NOTE: This method will not return an object when
    # passed constraints that are reference types!
    def findmany(self, num_elements=None, page_size=None, page=None, start=None, end=None, sort_fields=None,
                 search=None, search_fields=None, **constraints):
        """
        Finds and returns a list of (valid) documents.

        Arguments:
            num_elements (int): The number of documents to limit the result size to (used without paging).
            page_size (int): The number of documents to include per paginated result (used with page).
            page (int): The page number to return.
            start (int): The index to start on, inclusive (used without paging).
            end (int): The index to end on, inclusive (used without paging, with start).
            sort_fields (param[]): The document fields to sort results by.
            search (string): A text search for documents' fields.
            search_fields (param[]): The document fields to text search by.
            constraints (param[]): The constraints to apply to the find operation.

        Returns:
            A list of all documents satisfying the constraints provided.
        """

        with self.conn():
            # Do text search or grab by constraints
            if search is not None:
                ret = self._text_search(search, fields=search_fields)
            else:
                ret = self.dto.objects(Q(**constraints) & self._valid_query())

            # Sort if there are sort fields
            if sort_fields is not None and len(sort_fields) > 0:
                ret = ret.order_by(*sort_fields)

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

    # Query to get all valid objects
    def _valid_query(self):
        return Q()

    # Search string fields for text and return list of results
    def _text_search(self, text, fields):
        # Search default fields if none given
        if fields is None:
            fields = self._default_search_fields()
        entry_query = self._get_query(text, fields)
        found_entries = self.dto.objects(entry_query & self._valid_query())
        return found_entries

    # Create search term list from search string
    def _normalize_query(self, query_string,
                         findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                         normspace=re.compile(r'\s{2,}').sub):
        return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]

    # Get a query representing text search results
    def _get_query(self, query_string, search_fields):
        query = None  # Query to search for every search term
        terms = self._normalize_query(query_string)
        for term in terms:
            or_query = None
            for field_name in search_fields:
                q = self._term_query(term, field_name)
                or_query = or_query | q if or_query else q
            query = query & or_query if query else or_query
        return query

    # Get a Q searching for a single term
    def _term_query(self, term, field_name):
        return Q(**{'%s__icontains' % field_name: term})

    # Default search fields: all string fields
    def _default_search_fields(self):
        return [key for key, value in self.dto._fields.iteritems() if isinstance(value, StringField)]


class ContactDAO(DAO):
    """A DAO for the Contact document."""

    def __init__(self):
        super(ContactDAO, self).__init__()
        self.dto = ContactDTO

        # Injected dependencies
        self.org_dao = OrganizationDAO
        self.pub_dao = PublicationDAO
        # Weights for search result fields
        # The more content that is filled, the higher ranked the search
        self._field_weights = {
            'first_name': 0.1,
            'last_name': 0.1,
            'phones': 0.2,
            'email': 0.2,
            'organization': 0.1,
            'publications': 0.2,
            'position': 0.1,
            'valid': 0.0,
            'last_updated': 0.0,
            'updated_by': 0.0,
            'content_weight': 0.0,
        }

    def _add_contact_ref_to_children(self, contact_dto):
        if contact_dto.organization is not None and contact_dto not in contact_dto.organization.contacts:
            contact_dto.organization.contacts.append(contact_dto)
            contact_dto.organization = self.org_dao().create_update(contact_dto.organization, False)
        if contact_dto.publications is not None:
            for i in range(len(contact_dto.publications)):
                p = contact_dto.publications[i]
                if contact_dto not in p.authors:
                    p.authors.append(contact_dto)
                    contact_dto.publications[i] = self.pub_dao.create_update(p, False)
        return contact_dto

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

            if no_id:
                existing_dto = self.dto.objects(email=contact_dto.email).first()
                if existing_dto is not None:
                    saved_dto = self.merge_documents(existing_dto, contact_dto)
                    if cascade_add:
                        saved_dto = self._add_contact_ref_to_children(saved_dto)
                    return saved_dto
            contact_dto.last_updated = datetime.utcnow()
            self._update_weights(contact_dto)
            contact_dto.save()
        return contact_dto

    def _update_weights(self, contact_dto):
        weight = 0.0
        for key in contact_dto._data:
            if key == "id":
                continue
            if not hasattr(contact_dto, key):
                continue

            val = getattr(contact_dto, key)
            if val:
                weight += self._field_weights[key]

        contact_dto.content_weight = weight

    def _default_search_fields(self):
        return ['first_name', 'last_name', 'position', ]


class OrganizationDAO(DAO):
    """A DAO for the Organization document."""

    def __init__(self):
        super(OrganizationDAO, self).__init__()
        self.dto = OrganizationDTO

        # Injected dependencies
        self.contact_dao = ContactDAO
        self.geocode = geocode

        # Weights for search result fields
        # The more content that is filled, the higher ranked the search
        self._field_weights = {
            'name': 0.1,
            'address': 0.05,
            'latlng': 0.05,
            'types': 0.1,
            'phone_numbers': 0.1,
            'email_key': 0.0,
            'emails': 0.1,
            'contacts': 0.1,
            'organization_url': 0.1,
            'partners': 0.1,
            'facebook': 0.05,
            'twitter': 0.05,
            'keywords': 0.1,
            'valid': 0.0,
            'last_updated': 0.0,
            'updated_by': 0.0,
            'page_rank_info': 0.0,
            'page_rank': 0.0,
            'page_rank_weight': 0.0,
            'content_weight': 0.0,
            'combined_weight': 0.0,
        }

    def merge_documents(self, existing_org_dto, new_org_dto):
        with self.conn():
            attributes = new_org_dto._data
            for key in attributes:
                if key == 'page_rank_info' and attributes['page_rank_info']:
                    new_val = self._merge_page_rank_info(attributes['page_rank_info'], existing_org_dto.page_rank_info,
                                         attributes['organization_url'])
                    existing_org_dto.page_rank_info = new_val
                elif attributes[key] or key == 'latlng':
                    cur_attr = getattr(existing_org_dto, key)
                    if not cur_attr:
                        if key == 'latlng' and not attributes['latlng'] and attributes['address']:
                            setattr(existing_org_dto, key, attributes[key])
                    elif type(cur_attr) is list:
                        merged_list = list(set(cur_attr + attributes[key]))
                        # if this is org types and we have more than one org type, make sure unknown isn't a type :P
                        if key == "types" and len(merged_list) > 1 and OrgTypesEnum.UNKNOWN in merged_list:
                            merged_list.remove(OrgTypesEnum.UNKNOWN)
                        setattr(existing_org_dto, key, attributes[key])

            existing_org_dto.last_updated = datetime.utcnow()
            existing_org_dto.save()
            return existing_org_dto

    def _merge_page_rank_info(self, new_references, existing_references, organization_url):
        if existing_references is None:
            return new_references

        org_domain = UrlUtility().get_domain(organization_url)
        for ref in new_references.references:
            ref_exists = False
            # Search for existing references from one organization to another
            for exist_ref in existing_references.references:
                if ref.org_domain == exist_ref.org_domain:
                    # We found existing data for references from Org A to Org B
                    ref_exists = True
                    for page in ref.pages:
                        page_exists = False
                        # Search if we have data from this specific URL to this specific organization
                        for exist_page in exist_ref.pages:
                            if page.url == exist_page.url:
                                # We found existing data for references from URL A to Org B
                                page_exists = True
                                count_diff = page.count - exist_page.count
                                if count_diff != 0:
                                    # This page must have changed b/c the number of references is different
                                    # update everything
                                    exist_page.count = page.count
                                    exist_ref.count += count_diff
                                    existing_references.total_with_self += count_diff
                                    if exist_ref.org_domain != org_domain:
                                        # This value only updated if Organization A and B are different
                                        existing_references.total += count_diff
                                break
                        if not page_exists:
                            # We have recorded other references to this organization, but none from this url
                            exist_ref.pages.append(page)
                            exist_ref.count += page.count
                            existing_references.total_with_self += page.count
                            if exist_ref.org_domain != org_domain:
                                existing_references.total += page.count
                    break
            # If this organization has not yet referenced the specified outside org, add it
            if not ref_exists:
                existing_references.references.append(ref)
                existing_references.total_with_self += ref.count
                if ref.org_domain != org_domain:
                    existing_references.total += ref.count
        return existing_references

    def _add_org_ref_to_children(self, org_dto):
        for i in range(len(org_dto.contacts)):
            c = org_dto.contacts[i]
            if c.organization is None:
                c.organization = org_dto
                org_dto.contacts[i] = self.contact_dao().create_update(c, False)
        for i in range(len(org_dto.partners)):
            p = org_dto.partners[i]
            if org_dto not in p.partners:
                p.partners.append(org_dto)
                org_dto.partners[i] = self.create_update(p, False)
        return org_dto

    def create_update(self, org_dto, cascade_add=True):
        no_id = org_dto.id is None
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

            if no_id:
                existing_dto = self._smart_search_orgs(org_dto)
                if existing_dto is not None:
                    saved_dto = self.merge_documents(existing_dto, org_dto)
                    if cascade_add:
                        saved_dto = self._add_org_ref_to_children(saved_dto)
                    return saved_dto
                elif org_dto.latlng is None and org_dto.address:
                    # Geocode it
                    org_dto.latlng = self.geocode(org_dto.address)

            org_dto.last_updated = datetime.utcnow()
            self._update_weights(org_dto)
            org_dto.save()
            if cascade_add:
                org_dto = self._add_org_ref_to_children(org_dto)
        return org_dto

    def _update_weights(self, org_dto):
        weight = 0.0
        for key in org_dto._data:
            if key == "id":
                continue
            if not hasattr(org_dto, key):
                continue

            val = getattr(org_dto, key)
            if val:
                weight += self._field_weights[key]
        if org_dto.page_rank_weight is None:
            org_dto.page_rank_weight = 0.0

        org_dto.content_weight = weight
        org_dto.combined_weight = (org_dto.page_rank_weight + org_dto.content_weight) / 2.0

    # Query getting valid organizations: must be valid and have a valid name
    def _valid_query(self):
        return Q(name__ne=None) & Q(name__ne='')

    # Query searching for organizations by a single term
    def _term_query(self, term, field_name):
        q = None
        if field_name == 'types':
            types = OrgTypesEnum.mapping.keys()
            matches = [OrgTypesEnum.mapping[type] for type in types if term.lower() in type.lower()]
            for match in matches:
                new_query = Q(types=match)
                q = q | new_query if q else new_query
        else:
            q = super(OrganizationDAO, self)._term_query(term, field_name)

        return q

    # Default fields for organization text searching
    def _default_search_fields(self):
        return ['name', 'keywords', 'address', 'types', ]

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

        # organizations have unique names
        if org_dto.name:
            same_name = Q(name=org_dto.name)
        else:
            same_name = Q()

        existing_dto = self.dto.objects(same_phone | same_email | same_url | same_fb | same_twitter | same_name).first()
        return existing_dto

    def page_rank_store(self, org_dtos, store_info=False):
        """
        A method for storing a list of org_dtos' new page_rank information
        NOTE: store_info should only be called if the spider wasn't running during calculation process,
        otherwise we might overwrite new page_rank_info

        org_dtos - The organization DTOs to store page rank information for.
        store_info - Whether or not we should store new page_rank_info.
        """

        with self.conn():
            for i in range(0, len(org_dtos)):
                dto = org_dtos[i]
                try:
                    if not store_info:
                        exist_dto = self.find(id=dto.id)
                        exist_dto.page_rank = dto.page_rank
                        exist_dto.page_rank_weight = dto.page_rank_weight
                        self._update_weights(exist_dto)
                        exist_dto.save()
                    else:
                        exist_dto = self.find(id=dto.id)
                        exist_dto.page_rank = dto.page_rank
                        exist_dto.page_rank_weight = dto.page_rank_weight
                        exist_dto.page_rank_info = dto.page_rank_info
                        self._update_weights(exist_dto)
                        exist_dto.save()
                except Exception as e:
                    # Something goofy happened but rolling back's not really an option
                    print "ERROR: Failed to store DTO: {" +\
                        "\n\t id: " + str(dto.id) +\
                        "\n} with exception: \n\n" + e.message


class PublicationDAO(DAO):
    """A DAO for the Publication document."""

    def __init__(self):
        super(PublicationDAO, self).__init__()
        self.dto = PublicationDTO

        # Injected dependencies
        self.contact_dao = ContactDAO

    def create_update(self, pub_dto, cascade_add=True):
        no_id = pub_dto.id is None
        with self.conn():
            if no_id:
                existing_dto = self.dto.objects(title=pub_dto.title).first()
                if existing_dto is not None:
                    saved_dto = self.merge_documents(existing_dto, pub_dto)
                    return saved_dto

            pub_dto.last_updated = datetime.utcnow()
            pub_dto.save()
        return pub_dto

    def _default_search_fields(self):
        return ['title', 'authors', ]


class URLMetadataDAO(DAO):
    """A DAO for the URLMetadata document."""

    def __init__(self):
        super(URLMetadataDAO, self).__init__()
        self.dto = URLMetadataDTO

    def merge_documents(self, dto, merge_dto):
        with self.conn():
            attributes = merge_dto._data
            for key in attributes:
                if key == "last_visited":
                    cur_attr = getattr(dto, key)
                    if attributes[key] > cur_attr:
                        setattr(dto, key, attributes[key])
                elif attributes[key] is not None:
                    setattr(dto, key, attributes[key])
            dto.save()
            return dto

    def create_update(self, url_dto):
        with self.conn():
            if url_dto.id is None:
                existing_dto = self.dto.objects(url=url_dto.url).first()
                if existing_dto is not None:
                    saved_dto = self.merge_documents(existing_dto, url_dto)
                    return saved_dto

            url_dto.last_updated = datetime.utcnow()
            url_dto.save()
        return url_dto

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


class UserDAO(DAO):
    def __init__(self):
        super(UserDAO, self).__init__()
        self.dto = UserDTO

        # Injected dependencies
        self.org_dao = OrganizationDAO
        # Weights for search result fields
        # The more content that is filled, the higher ranked the search
        self._field_weights = {
            'first_name': 0.1,
            'last_name': 0.1,
            'email': 0.2,
            'password': 0.0,
            'background': 0.2,
            'account_type': 0.1,
            'org_type': 0.1,
            'organization': 0.2,
            'last_updated': 0.0,
            'content_weight': 0.0,
        }

    def create_update(self, user_dto):
        with self.conn():
            if user_dto.organization is not None:
                o = user_dto.organization
                user_dto.organization = self.org_dao().create_update(o)

            user_dto.last_updated = datetime.utcnow()
            self._update_weights(user_dto)
            user_dto.save()
        return user_dto

    def _update_weights(self, user_dto):
        weight = 0.0
        for key in user_dto._data:
            if key == "id":
                continue
            if not hasattr(user_dto, key):
                continue

            val = getattr(user_dto, key)
            if val:
                weight += self._field_weights[key]

        user_dto.content_weight = weight
