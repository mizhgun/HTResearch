from HTResearch.Utilities.logutil import LoggingSection, get_logger
from pymongo.errors import AutoReconnect
import time

logger = get_logger(LoggingSection.CLIENT, __name__)

def safe_mongocall(call):
      def _safe_mongocall(*args, **kwargs):
        for i in xrange(5):
          try:
            return call(*args, **kwargs)
          except AutoReconnect:
            time.sleep(pow(2, i))
        logger.error('Exception while connecting to Mongo. Retrying...')
      return _safe_mongocall