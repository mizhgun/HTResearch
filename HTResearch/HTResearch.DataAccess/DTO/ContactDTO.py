from mongoengine import *

class ContactDTO(Document):
    """description of class"""
    first_name = StringField()
    last_name = StringField()
    primary_phone = IntField()
    secondary_phone = StringField()
    email = EmailField()