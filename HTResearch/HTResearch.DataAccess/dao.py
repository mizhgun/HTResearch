from dto import *
from mongoengine import connect, disconnect

class ContactDAO(object):
    """A DAO for the Contact document"""

    def Create(self, contact_dto):
        connect('researchData')
        contact_dto.save()
        disconnect()

    def Delete(self, contact_dto):
        connect('researchData')
        contact_dto.delete()
        disconnect()

    def Edit(self, contact_dto):
        connect('researchData')
        old_dto = ContactDTO.objects(id=contact_dto.id).first()
        old_dto = contact_dto
        old_dto.save()
        disconnect()

    def Find(self, dto_id):
        return ContactDTO.objects(id=dto_id).first()

class OrganizationDAO(object):
    """A DAO for the Organization document"""

    def Create(self, org_dto):
        connect('researchData')
        org_dto.save()
        disconnect()

    def Delete(self, org_dto):
        connect('researchData')
        org_dto.delete()
        disconnect()

    def Edit(self, org_dto):
        connect('researchData')
        old_dto = OrganizationDTO.objects(id=org_dto.id).first()
        old_dto = org_dto
        old_dto.save()
        disconnect()

    def Find(self, dto_id):
        return OrganizationDTO.objects(id=dto_id).first()

class PublicationDAO(object):
    """A DAO for the Publication document"""

    def Create(self, pub_dto):
        connect('researchData')
        pub_dto.save()
        disconnect()

    def Delete(self, pub_dto):
        connect('researchData')
        pub_dto.delete()
        disconnect()

    def Edit(self, pub_dto):
        connect('researchData')
        old_dto = PublicationDTO.objects(id=pub_dto.id).first()
        old_dto = pub_dto
        old_dto.save()
        disconnect()

    def Find(self, dto_id):
        return PublicationDTO.objects(id=dto_id).first()