import csv
from HTResearch.DataAccess.dto import *
from HTResearch.DataAccess.dao import *
from HTResearch.DataAccess.factory import DAOFactory
from HTResearch.DataModel.model import *
from HTResearch.DataModel.converter import DTOConverter
from HTResearch.DataAccess.connection import DBConnection


with DBConnection() as c:
    c.dropall()

path = 'C:\Users\Aubrey\Documents\Organizations.csv'

with open(path, 'rb') as csv_file:
    reader = csv.reader(csv_file)
    for row in reader:
        print row
        phone_numbers = (unicode(row[3], errors='ignore')).split("'")
        emails = (unicode(row[4], errors='ignore')).split("'")
        new_org = Organization(name=unicode(row[0], errors='ignore'),
                               organization_url=unicode(row[1], errors='ignore'),
                               address=unicode(row[2], errors='ignore'),
                               phone_numbers=phone_numbers,
                               emails=emails)
        if emails[0]:
            new_org.email_key = emails[0]
        if unicode(row[5], errors='ignore'):
            new_org.facebook = unicode(row[5], errors='ignore')
        if unicode(row[6], errors='ignore'):
            new_org.twitter = unicode(row[6], errors='ignore')
        org_dto = DTOConverter.to_dto(OrganizationDTO, new_org)
        org_dao = DAOFactory.get_instance(OrganizationDAO)
        org_dao.create_update(org_dto)



