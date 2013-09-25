import sys
[sys.path.remove(p) for p in sys.path if 'DataAccess' in p]

sys.path.append('../DataAccess/')

import dto

class DTOConverter(object):
    """A class for converting base objects to and from DTOs."""

    @staticmethod
    def from_dto(cls, obj):
        new_cls = cls()
        [setattr(new_cls, key, obj._data[key]) for key in obj._data if key != 'id']
        return new_cls

    @staticmethod
    def to_dto(cls, obj):
        new_dto = cls()
        [setattr(new_dto, attr, value) for attr, value in obj.__dict__.iteritems()]
        return new_dto