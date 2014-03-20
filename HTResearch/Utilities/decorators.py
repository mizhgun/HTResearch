from HTResearch.Utilities.logutil import LoggingSection, get_logger
from pymongo.errors import AutoReconnect
import time

#region Globals
logger = get_logger(LoggingSection.CLIENT, __name__)
#endregion

def safe_mongocall(call):
    """
    A Mongo call wrapper to better handle exceptions

    @param call:
        Any Mongo/Mongoengine accessor function that risks throwing an AutoReconnect Exception
    @return:
        The original function
    """
    def _safe_mongocall(*args, **kwargs):
        for i in xrange(5):
            try:
                return call(*args, **kwargs)
            except AutoReconnect:
                time.sleep(pow(2, i))
                logger.error('Exception while connecting to Mongo. Retrying...')
    return _safe_mongocall

def safe_apicall(call):
    """
    Catches unhandled exceptions in non-view API functions

    @param call:
        Any API function that does not trigger Circular Reference exceptions when wrapped

    @return:
        The original function
    """
    def _safe_apicall(*args, **kwargs):
        try:
            return call(*args, **kwargs)
        except Exception, e:
            logger.error(e.message)

    return _safe_apicall