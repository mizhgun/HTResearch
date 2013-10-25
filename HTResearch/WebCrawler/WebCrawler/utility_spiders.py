### Module for ad hoc spiders ###

import os
import pickle

from scrapy.spider import BaseSpider
from scrapy.http import Response

OUTPUT_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Output')


class DebugFileGenerator(BaseSpider):
    """A spider to store responses to files for later use (such as for unit tests)"""
    name = 'debug_file_generator'
    allowed_domains = []
    start_urls = []  # passed in by command

    def __init__(self, *args, **kwargs):
        super(DebugFileGenerator, self).__init__(*args, **kwargs)

    def parse(self, response):
        # create filename from url
        filename = "".join([c for c in response.url if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
        with open(os.path.join(OUTPUT_DIRECTORY, filename), mode='w') as to_write:
            pickle.dump(response, to_write)

