from DataAccess import dto

class DTOConverter(object):
    """A class for converting base objects to and from DTOs."""

    @staticmethod
    def from_dto(cls, obj):
        new_cls = cls()
        for attr, value in obj.__dict__.iteritems():
            new_cls.attr = value

    @staticmethod
    def to_dto(cls, obj):
        new_dto = cls()
        for attr, value in obj.__dict__.iteritems():
            new_dto.attr = value