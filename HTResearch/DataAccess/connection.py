# stdlib imports
from mongoengine.connection import connect, disconnect, get_connection
from pymongo.son_manipulator import SON

# project imports
from HTResearch.Utilities.config import get_config_value
from HTResearch.Utilities.logutil import LoggingSection, get_logger

#region Globals
logger = get_logger(LoggingSection.DATA, __name__)
#endregion


class DBConnection(object):
    """A class that encapsulates the MongoDB connection"""

    def __init__(self):
        try:
            host = get_config_value("MONGO", "host")
            port = int(get_config_value("MONGO", "port"))
            name = get_config_value("MONGO", "name")
            disconnect()
            connect(db=name, host=host, port=port)
            self.conn = get_connection()
            pass
        except:
            logger.error('Connection to MongoDB could not be established.')

    def __enter__(self):
        return self

    def __exit__(self, ext, exv, trb):
        disconnect()
