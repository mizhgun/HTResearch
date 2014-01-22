# stdlib imports
import unittest

# project imports
from HTResearch.Utilities.logutil import get_logger, LoggingSection


class LoggingUtilityTest(unittest.TestCase):
    def test_logging(self):
        logger = get_logger(LoggingSection.TEST, __name__)

        logger.debug("Logging some debug info.")
        logger.info("Logging some info.")
        logger.warning("Logging a warning.")
        logger.critical("Logging a critical error.")

        print 'Logging tests passed'


if __name__ == '__main__':
    unittest.main()