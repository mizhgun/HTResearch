from DataModel.model import *


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
                elif key == 'organizations':
                    setattr(new_model, key, [ModelConverter.to_model(Organization, o) for o in value])
                elif key == 'publications':
                    setattr(new_model, key, [ModelConverter.to_model(Publication, p) for p in value])
                else:
                    setattr(new_model, key, value)
        return new_model