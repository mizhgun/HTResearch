from dto import *

class ContactDAO(Object):
    """A DAO for the Contact document"""

    @classmethod
    def Create(cls, contact_dto):
        contact_dto.save()

    @classmethod
    def Delete(cls, contact_dto):
        contact_dto.delete()

    @classmethod
    def Edit(cls, contact_dto):
        old_dto = ContactDTO.objects(id=contact_dto.id).first()
        old_dto = contact_dto
        old_dto.save()
    
    @classmethod
    def Find(cls, dto_id):
        return ContactDTO.objects(id=dto_id).first()

class OrganizationDAO(Object):
    """A DAO for the Organization document"""

    @classmethod
    def Create(cls, org_dto):
        org_dto.save()

    @classmethod
    def Delete(cls, org_dto):
        org_dto.delete()

    @classmethod
    def Edit(cls, org_dto):
        old_dto = OrganizationDTO.objects(id=org_dto.id).first()
        old_dto = org_dto
        old_dto.save()
    
    @classmethod
    def Find(cls, dto_id):
        return OrganizationDTO.objects(id=dto_id).first()

class PublicationDAO(Object):
    """A DAO for the Publication document"""

    @classmethod
    def Create(cls, pub_dto):
        pub_dto.save()

    @classmethod
    def Delete(cls, pub_dto):
        pub_dto.delete()

    @classmethod
    def Edit(cls, pub_dto):
        old_dto = PublicationDTO.objects(id=pub_dto.id).first()
        old_dto = pub_dto
        old_dto.save()
    
    @classmethod
    def Find(cls, dto_id):
        return PublicationDTO.objects(id=dto_id).first()