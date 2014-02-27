import sys
from  HTResearch.DataAccess.dao import ContactDAO, OrganizationDAO, UserDAO


org_dao = OrganizationDAO()
all_orgs = org_dao.all()
for dto in all_orgs:
    org_dao.create_update(dto)

con_dao = ContactDAO()
all_cons = con_dao.all()
for dto in all_cons:
    con_dao.create_update(dto)

usr_dao = UserDAO()
all_usrs = usr_dao.all()
for dto in all_usrs:
    usr_dao.create_update(dto)

sys.exit(0)
