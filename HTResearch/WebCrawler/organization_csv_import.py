import csv
from HTResearch.DataAccess.dto import *
from HTResearch.DataAccess.dao import *
from HTResearch.DataAccess.factory import DAOFactory
from HTResearch.DataModel.model import *
from HTResearch.DataModel.converter import DTOConverter


with open('C:\Users\s-athomp44\Documents\organization.csv') as csv_file:
    reader = csv.reader(csv_file)
    for row in reader:
        new_org = Organization(name=row[0],
                               organization_url=row[1],
                               address=row[2].replace(u'\xa0', u' '),
                               phone_number=row[3],
                               email=row[4])
        org_dto = DTOConverter.to_dto(OrganizationDTO, new_org)
        org_dao = DAOFactory.get_instance(OrganizationDAO)
        org_dao.create_update(org_dto)



