from HTResearch.Utilities.data_structures import enum

AccountType = enum(
    'COLLABORATOR',
    'CONTRIBUTOR',
)

OrgTypesEnum = enum(
    ### THIS IS AN ORDERED LIST. IF ADDING A TYPE ADD TO THE BOTTOM ###
    ### DON'T ADD TO THE TOP, ADD TO THE BOTTOM ###
    'GOVERNMENT',
    'RELIGIOUS',
    'EDUCATION',
    'ADVOCACY',
    'RESEARCH',
    'PREVENTION',
    'PROTECTION',
    'PROSECUTION',
    'UNKNOWN',
    ### ADD NEW TYPES ABOVE THIS LINE ###
)