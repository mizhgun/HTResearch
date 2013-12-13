import logging
import logging.handlers
import os
import time

from data_structures import enum
from config import get_config_value


LoggingSection = enum(
    'CLIENT',
    'CRAWLER',
    'DATA',
    'FRONTIER',
    'TEST',
    'UTILITIES',
)

#region Setup
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s %(levelname)s] %(name)s::%(funcName)s - %(message)s',
                    datefmt='%x %X %Z')
module_dir = os.path.dirname(__file__)
logfile = os.path.join(module_dir, get_config_value('LOG', 'path'))
logdir = os.path.join(module_dir, get_config_value('LOG', 'dir'))

if not os.path.exists(logdir):
    os.mkdir(logdir)


handler = logging.handlers.RotatingFileHandler(logfile,
                                               maxBytes=8192,
                                               backupCount=10,)
formatter = logging.Formatter('[%(asctime)s %(levelname)s] %(name)s::%(funcName)s - %(message)s')
formatter.datefmt = '%x %X %Z'
formatter.converter = time.gmtime
handler.setFormatter(formatter)
#endregion


def get_logger(section, name):
    section_name = LoggingSection.reverse_mapping[section].lower()

    logger = logging.getLogger('htresearch.{0}.{1}'.format(section_name, name))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger