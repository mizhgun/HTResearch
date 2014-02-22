from HTResearch.DataModel.model import *
from HTResearch.DataAccess.dto import *
from HTResearch.DataAccess.dao import *


class DTOConverter(object):
    """A class for converting base objects to and from DTOs."""

    @staticmethod
    def from_dto(cls, obj):
        if obj is None:
            return None

        if not hasattr(obj, '_data'):
            return None

        new_cls = cls()

        for key in obj._data:
            if key == 'contacts':
                setattr(new_cls, key, [DTOConverter.from_dto(Contact, c) for c in obj._data[key]])
            elif key == 'organization' and obj._data[key] is not None:
                setattr(new_cls, key, DTOConverter.from_dto(Organization, obj._data[key]))
            elif key == 'publications':
                setattr(new_cls, key, [DTOConverter.from_dto(Publication, p) for p in obj._data[key]])
            elif key == 'page_rank_info':
                setattr(new_cls, key, DTOConverter.from_dto(PageRankInfo, obj._data[key]))
            elif key == 'references':
                setattr(new_cls, key, [DTOConverter.from_dto(PageRankVector, v) for v in obj._data[key]])
            elif key == 'pages':
                setattr(new_cls, key, [DTOConverter.from_dto(UrlCountPair, ucp) for ucp in obj._data[key]])
            else:
                if key != 'id':
                    setattr(new_cls, key, obj._data[key])
        return new_cls

    @staticmethod
    def to_dto(cls, obj):
        new_dto = cls()

        for key, value in obj.__dict__.iteritems():
            if key == 'contacts':
                setattr(new_dto, key, [DTOConverter.to_dto(ContactDTO, c) for c in value])
            elif key == 'organization' and value is not None:
                setattr(new_dto, key, DTOConverter.to_dto(OrganizationDTO, value))
            elif key == 'partners':
                setattr(new_dto, key, [DTOConverter.to_dto(OrganizationDTO, o) for o in value])
            elif key == 'publications':
                setattr(new_dto, key, [DTOConverter.to_dto(PublicationDTO, p) for p in value])
            elif key == 'page_rank_info':
                if value:
                    setattr(new_dto, key, DTOConverter.to_dto(PageRankInfoDTO, value))
                else:
                    setattr(new_dto, key, value)
            elif key == 'references':
                if value:
                    setattr(new_dto, key, [DTOConverter.to_dto(PageRankVectorDTO, v) for v in value])
                else:
                    setattr(new_dto, key, [])
            elif key == 'pages':
                if value:
                    setattr(new_dto, key, [DTOConverter.to_dto(UrlCountPairDTO, ucp) for ucp in value])
                else:
                    setattr(new_dto, key, [])
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
                if key == 'contacts':
                    setattr(new_model, key, [ModelConverter.to_model(Contact, c) for c in value])
                elif key == 'organization':
                    setattr(new_model, key, ModelConverter.to_model(Organization, value))
                elif key == 'partners':
                    setattr(new_model, key, [ModelConverter.to_model(Organization, o) for o in value])
                elif key == 'publications':
                    setattr(new_model, key, [ModelConverter.to_model(Publication, p) for p in value])
                elif key == 'page_rank_info':
                    setattr(new_model, key, ModelConverter.to_model(PageRankInfo, value))
                elif key == 'references':
                    setattr(new_model, key, [ModelConverter.to_model(PageRankVector, v) for v in value])
                elif key == 'pages':
                    setattr(new_model, key, [ModelConverter.to_model(UrlCountPair, ucp) for ucp in value])
                else:
                    setattr(new_model, key, value)
        return new_model