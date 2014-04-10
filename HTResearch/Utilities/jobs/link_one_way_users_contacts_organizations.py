import sys
from HTResearch.DataAccess.dao import *

org_dao = OrganizationDAO()
contact_dao = ContactDAO()
user_dao = UserDAO()

all_orgs = org_dao.all()
for dto in all_orgs:
    if dto.contacts:
        for contact in dto.contacts:
            if contact.organization != dto:
                contact.organization = dto
                contact_dao.create_update(contact)

    if dto.user_contacts:
        for user in dto.user_contacts:
            if user.organization != dto:
                user.organization = dto
                user_dao.create_update(user)

all_contacts = contact_dao.all()
for dto in all_contacts:
    if dto.organization and not dto in dto.organization.contacts:
        dto.organization.contacts.append(dto)
        org_dao.create_update(dto.organization)

all_users = user_dao.all()
for dto in all_users:
    if dto.organization and not dto in dto.organization.user_contacts:
        dto.organization.user_contacts.append(dto)
        org_dao.create_update(dto.organization)

sys.exit(0)
