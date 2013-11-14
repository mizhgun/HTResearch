import json
from mongoengine.fields import ObjectId, StringField, URLField
from HTResearch.DataModel.model import *
from HTResearch.DataAccess.dto import *
from UserString import MutableString


class MongoJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        elif isinstance(o, list) and len(o) > 0 and all(
                isinstance(x, (
                    Contact, ContactDTO, Organization, OrganizationDTO, Publication, PublicationDTO, URLMetadata,
                    URLMetadataDTO)) for x in o):
            new_list = []
            for item in list:
                new_list.append(self.encode_ref(item))
            return new_list
        elif isinstance(o, (
            Contact, ContactDTO, Organization, OrganizationDTO, Publication, PublicationDTO, URLMetadata,
            URLMetadataDTO)):
            return self.encode_ref(o)
        return json.JSONEncoder.default(self, o)

    def encode(self, o):
        result = super(MongoJSONEncoder, self).encode(o)
        if isinstance(o, ObjectId):
            result = result[1:-1]
        return result

    def encode_ref(self, o):
        # Convert objects to a dictionary of their representation
        d = {'__class__': o.__class__.__name__,
             '__module__': o.__module__,
        }
        d.update(o.__dict__)
        return d
