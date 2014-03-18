#
# enums.py
# A module containing the various enums used throughout the project.
#


from HTResearch.Utilities.data_structures import enum

AccountType = enum(
    'COLLABORATOR',
    'CONTRIBUTOR',
)

OrgTypesEnum = enum(
    ### THIS IS AN ORDERED LIST. IF ADDING A TYPE ADD TO THE BOTTOM ###
    ### DON'T ADD TO THE TOP, ADD TO THE BOTTOM ###
    'GOVERNMENT', #0
    'RELIGIOUS',  #1
    'EDUCATION',  #2
    'ADVOCACY',   #3
    'RESEARCH',   #4
    'PREVENTION', #5
    'PROTECTION', #6
    'PROSECUTION',#7
    'UNKNOWN',    #8
    ### ADD NEW TYPES ABOVE THIS LINE ###
)