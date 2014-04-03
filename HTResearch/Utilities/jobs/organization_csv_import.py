import csv
import os
from HTResearch.DataAccess.dao import *
from HTResearch.DataAccess.factory import DAOFactory
from HTResearch.DataModel.model import *
from HTResearch.DataModel.converter import DTOConverter

dir = os.getcwd()
path = dir+'\Orgs.csv'

with open(path, 'rb') as csv_file:
    reader = csv.reader(csv_file)
    for row in reader:
        print row
        new_org = Organization(name=unicode(row[0], errors='ignore'),
                               organization_url=unicode(row[1], errors='ignore'),
                               address=unicode(row[2], errors='ignore'))
        if row[3]:
            new_org.phone_numbers = (unicode(row[3], errors='ignore')).split("'")
        if row[4]:
            new_org.emails = (unicode(row[4], errors='ignore')).split("'")
            if new_org.emails[0]:
                new_org.email_key = new_org.emails[0]
        if row[7]:
            new_org.types = (unicode(row[7], errors='ignore')).split(",")
        if unicode(row[5], errors='ignore'):
            new_org.facebook = unicode(row[5], errors='ignore')
        if unicode(row[6], errors='ignore'):
            new_org.twitter = unicode(row[6], errors='ignore')
        org_dto = DTOConverter.to_dto(OrganizationDTO, new_org)
        org_dao = DAOFactory.get_instance(OrganizationDAO)
        org_dao.create_update(org_dto)



