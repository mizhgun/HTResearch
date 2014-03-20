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

    Arguments:
        section (string): The section the value is stored under.
        key (string): The key associated with the value.

    Returns:
        A string for the config value, or None.
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


    Arguments:
        section (string): The section values are stored under.

    Returns:
        A (string, string) dictionary for all keys and values under the section, or None.
    """
    try:
        parser = ConfigParser.ConfigParser()
        parser.read(CONFIG_PATH)

        return dict(parser.items(section=section))
    except:
        return None