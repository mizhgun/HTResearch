import logging
import os

from types import Singleton
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


class LoggingUtility(object):
    """
    Provides a unified means of interacting with Python's logging module.
    This class is necessary to reduce code redundancy when specifying the
    basic configuration of Python's logging utility.
    """

    __metaclass__ = Singleton

    def __init__(self):
        dir = os.path.dirname(__file__)
        logfile = os.path.join(dir, get_config_value('LOG', 'path'))
        logdir = os.path.join(dir, get_config_value('LOG', 'dir'))
        if not os.path.exists(logdir):
            os.mkdir(logdir)

        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename=logfile,
                            filemode='w+')

    def get_logger(self, section, name):
        section_name = LoggingSection.reverse_mapping[section].lower()
        return logging.getLogger('htresearch.{0}.{1}'.format(section_name, name))