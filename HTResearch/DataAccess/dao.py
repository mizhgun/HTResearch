from dto import ContactDTO, OrganizationDTO, PublicationDTO

class ContactDAO(object):
    """A DAO for the Contact document"""

    def Create(self, contact_dto):
        contact_dto.save()

    def Delete(self, contact_dto):
        contact_dto.delete()

    def Edit(self, contact_dto):
        old_dto = ContactDTO.objects(id=contact_dto.id).first()
        old_dto = contact_dto
        old_dto.save()

    def Find(self, dto_id):
        return ContactDTO.objects(id=dto_id).first()

class OrganizationDAO(object):
    """A DAO for the Organization document"""

    def Create(self, org_dto):
        org_dto.save()

    def Delete(self, org_dto):
        org_dto.delete()

    def Edit(self, org_dto):
        old_dto = OrganizationDTO.objects(id=org_dto.id).first()
        old_dto = org_dto
        old_dto.save()

    def Find(self, dto_id):
        return OrganizationDTO.objects(id=dto_id).first()

class PublicationDAO(object):
    """A DAO for the Publication document"""

    def Create(self, pub_dto):
        pub_dto.save()

    def Delete(self, pub_dto):
        pub_dto.delete()

    def Edit(self, pub_dto):
        old_dto = PublicationDTO.objects(id=pub_dto.id).first()
        old_dto = pub_dto
        old_dto.save()

    def Find(self, dto_id):
        return PublicationDTO.objects(id=dto_id).first()

class URLMetadataDAO(object):
    """A DAO for the URLMetadata document"""

    def Create(self, url_dto):
        url_dto.save()

    def Delete(self, url_dto):
        url_dto.delete()

    def Edit(self, url_dto):
        old_dto = URLMetadataDTO.objects(id=url_dto.id).first()
        old_dto = url_dto
        old_dto.save()

    def Find(self, dto_id):
        return URLMetadataDTO.objects(id=dto_id).first()