import json
from mongoengine.fields import ObjectId, StringField, URLField
from HTResearch.DataModel.model import *
from HTResearch.DataAccess.dto import *
from UserString import MutableString


class MongoJSONEncoder(json.JSONEncoder):
    defined_types = (dict, list, tuple, str, unicode, int, long, float, bool, type(None))

    def default(self, o):
        # If ObjectId, cast to string
        if isinstance(o, ObjectId):
            return str(o)
        # If a list of any items that are custom objects, encode them ourselves
        elif isinstance(o, list) and len(o) > 0 and any(not self._check_if_encodable(x) for x in o):
            new_list = []
            for item in list:
                new_list.append(self._encode_ref(item))
            return new_list
        # If a custom object, encode ourselves
        elif not self._check_if_encodable(o):
            return self._encode_ref(o)
        # Otherwise, return
        return json.JSONEncoder.default(self, o)

    def encode(self, o):
        result = super(MongoJSONEncoder, self).encode(o)
        if isinstance(o, ObjectId):
            result = result[1:-1]
        return result

    def _encode_ref(self, o):
        # Convert objects to a dictionary of their representation
        d = {'__class__': o.__class__.__name__,
             '__module__': o.__module__,
        }
        d.update(o.__dict__)
        return d

    def _check_if_encodable(self, o):
        if isinstance(o, MongoJSONEncoder.defined_types):
            return True
        return False