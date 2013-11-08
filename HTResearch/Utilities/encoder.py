import json
from mongoengine.fields import ObjectId


class MongoJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

    def encode(self, o):
        result = super(MongoJSONEncoder, self).encode(o)
        if isinstance(o, ObjectId):
            result = result[1:-1]
        return result