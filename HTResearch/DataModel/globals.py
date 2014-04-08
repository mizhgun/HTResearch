#
# globals.py
# A module containing global resources that can be accessed from any package of the project.
#

# stdlib imports
from HTResearch.DataModel.enums import OrgTypesEnum

ORG_TYPE_CHOICES = ((OrgTypesEnum.GOVERNMENT, 'Government'),
                    (OrgTypesEnum.RELIGIOUS, 'Religious'),
                    (OrgTypesEnum.EDUCATION, 'Education'),
                    (OrgTypesEnum.ADVOCACY, 'Advocacy'),
                    (OrgTypesEnum.RESEARCH, 'Research'),
                    (OrgTypesEnum.NGO, "NGO"))