from HTResearch.DataModel.enums import OrgTypesEnum
from HTResearch.DataAccess.dao import OrganizationDAO

type_count = len(OrgTypesEnum.mapping)
org_dao = OrganizationDAO()
all_orgs = org_dao.all()
for dto in all_orgs:
    dto.types = [s for s in dto.types if s < type_count]
    org_dao.create_update(dto)

