#
# config.py
# A module that provides functions for interacting with config files.
#

import ConfigParser
import os

DIR = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(DIR, '../../htconfig.cfg')


def get_config_value(section, key):
    """
    Fetches a config value from htconfig.cfg as a string.

    section - The section the value is stored under.
    key - The key associated with the value.
    """
    try:
        parser = ConfigParser.ConfigParser()
        parser.read(CONFIG_PATH)

        return parser.get(section, key)
    except:
        return None


def get_section_values(section):
    """
    Fetches all config values within a certain section and returns them as a {key, value} dictionary.

    section - The section values are stored under.
    """
    try:
        parser = ConfigParser.ConfigParser()
        parser.read(CONFIG_PATH)

        return dict(parser.items(section=section))
    except:
        return None