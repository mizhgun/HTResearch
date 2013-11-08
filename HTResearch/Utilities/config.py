import ConfigParser
import os

DIR = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(DIR, '../../htconfig.cfg')


def get_config_value(section, key):
    parser = ConfigParser.ConfigParser()
    parser.read(CONFIG_PATH)

    return parser.get(section, key)