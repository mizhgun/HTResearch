#
# types.py
# A module containing custom types to be attributed to classes.
#


class Singleton(type):
    """An implementation of the Singleton pattern."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]