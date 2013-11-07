from HTResearch.DataModel.model import *
from HTResearch.DataAccess.dto import *


class DTOConverter(object):
    """A class for converting base objects to and from DTOs."""

    @staticmethod
    def from_dto(cls, obj):
        new_cls = cls()

        for key in obj._data:
            if key == 'contacts' or key == 'authors':
                setattr(new_cls, key, [DTOConverter.from_dto(Contact, c) for c in obj._data[key]])
            elif key == 'publisher' and obj._data[key] is not None:
                setattr(new_cls, key, DTOConverter.from_dto(Contact, obj._data[key]))
            elif key == 'organizations':
                setattr(new_cls, key, [DTOConverter.from_dto(Organization, o) for o in obj._data[key]])
            elif key == 'publications':
                setattr(new_cls, key, [DTOConverter.from_dto(Publication, p) for p in obj._data[key]])
            else:
                if key != 'id':
                    setattr(new_cls, key, obj._data[key])
        return new_cls

    @staticmethod
    def to_dto(cls, obj):
        new_dto = cls()

        for key, value in obj.__dict__.iteritems():
            if key == 'contacts' or key == 'authors':
                setattr(new_dto, key, [DTOConverter.to_dto(ContactDTO, c) for c in value])
            elif key == 'publisher' and value is not None:
                setattr(new_dto, key, DTOConverter.to_dto(ContactDTO, value))
            elif key == 'organizations':
                setattr(new_dto, key, [DTOConverter.to_dto(OrganizationDTO, o) for o in value])
            elif key == 'publications':
                setattr(new_dto, key, [DTOConverter.to_dto(PublicationDTO, p) for p in value])
            else:
                setattr(new_dto, key, value)
        return new_dto


class ModelConverter(object):
    """A class for converting items to Models."""

    @staticmethod
    def to_model(cls, obj):
        new_model = cls()

        for key, value in obj.iteritems():
            if value:
                if key == 'contacts' or key == 'authors':
                    setattr(new_model, key, [ModelConverter.to_model(Contact, c) for c in value])
                elif key == 'publisher' and value is not None:
                    setattr(new_model, key, ModelConverter.to_model(Contact, value))
                elif key == 'organizations' or key == 'partners':
                    setattr(new_model, key, [ModelConverter.to_model(Organization, o) for o in value])
                elif key == 'publications':
                    setattr(new_model, key, [ModelConverter.to_model(Publication, p) for p in value])
                else:
                    setattr(new_model, key, value)
        return new_model