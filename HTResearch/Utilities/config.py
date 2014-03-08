import ConfigParser
import os

DIR = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(DIR, '../../htconfig.cfg')


def get_config_value(section, key):
    try:
        parser = ConfigParser.ConfigParser()
        parser.read(CONFIG_PATH)

        return parser.get(section, key)
    except:
        return None


def get_section_values(section):
    try:
        parser = ConfigParser.ConfigParser()
        parser.read(CONFIG_PATH)

        return dict(parser.items(section=section))
    except:
        return None