from dto import *

class ContactDAO(Object):
    """A DAO for the Contact document"""

    def Create(cls, contact_dto):
        contact_dto.save()

    def Delete(cls, contactDTO):
        contact_dto.delete()

    def Edit(cls, contact_dto):
        old_dto = ContactDTO.objects(id=contact_dto.id).first()
        old_dto = contact_dto
        old_dto.save()
    
    def Find(cls, contact_dto):
        return ContactDTO.objects(id=contact_dto.id).first()

class OrganizationDAO(Object):
    """A DAO for the Organization document"""

    def Create(cls, org_dto):
        org_dto.save()

    def Delete(cls, org_dto):
        org_dto.delete()

    def Edit(cls, org_dto):
        old_dto = OrganizationDTO.objects(id=org_dto.id).first()
        old_dto = org_dto
        old_dto.save()
    
    def Find(cls, org_dto):
        return OrganizationDTO.objects(id=org_dto.id).first()

class PublicationDAO(Object):
    """A DAO for the Publication document"""

    def Create(cls, pub_dto):
        pub_dto.save()

    def Delete(cls, pub_dto):
        pub_dto.delete()

    def Edit(cls, pub_dto):
        old_dto = PublicationDTO.objects(id=pub_dto.id).first()
        old_dto = org_dto
        old_dto.save()
    
    def Find(cls, org_dto):
        return PublicationDTO.objects(id=pub_dto.id).first()