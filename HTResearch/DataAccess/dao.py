import sys
from dto import ContactDTO, OrganizationDTO, PublicationDTO, URLMetadataDTO

class ContactDAO(object):
    """A DAO for the Contact document"""

    def create_update(self, contact_dto):
        [OrganizationDAO().create_update(o) for o in contact_dto.organizations]
        [PublicationDAO().create_update(p) for p in contact_dto.publications]

        contact_dto.save()

    def delete(self, contact_dto):
        contact_dto.delete()

    def find(self, dto_id):
        return ContactDTO.objects(id=dto_id).first()

class OrganizationDAO(object):
    """A DAO for the Organization document"""

    def create_update(self, org_dto):
        [ContactDAO().create_update(c) for c in org_dto.contacts]

        org_dto.save()

    def delete(self, org_dto):
        org_dto.delete()

    def find(self, dto_id):
        return OrganizationDTO.objects(id=dto_id).first()

class PublicationDAO(object):
    """A DAO for the Publication document"""

    def create_update(self, pub_dto):
        [ContactDAO().create_update(c) for c in pub_dto.authors]

        if pub_dto.publisher is not None:
            ContactDAO().create_update(pub_dto.publisher)

        pub_dto.save()

    def delete(self, pub_dto):
        pub_dto.delete()

    def find(self, dto_id):
        return PublicationDTO.objects(id=dto_id).first()

class URLMetadataDAO(object):
    """A DAO for the URLMetadata document"""

    def create_update(self, url_dto):
        url_dto.save(cascade=True)

    def delete(self, url_dto):
        url_dto.delete()

    def find(self, dto_id):
        return URLMetadataDTO.objects(id=dto_id).first()