#
# url_tools.py
# A module containing tools for working with URLs.
#

# stdlib imports
from __future__ import with_statement
import os
from urlparse import urlparse

# project imports
from logutil import get_logger, LoggingSection
from types import Singleton

#region Globals
logger = get_logger(LoggingSection.UTILITIES, __name__)
#endregion


class UrlUtility:
    """A class for parsing and interacting with URLs."""
    __metaclass__ = Singleton

    tlds = None

    @staticmethod
    def _populate_tlds():
        with open(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources/effective_tld_names.dat.txt')) as f:
            UrlUtility.tlds = [line.strip().decode('utf-8') for line in f if line[0] not in "/\n"]

    @staticmethod
    def get_domain(url, no_exception=True):
        """
        Gets the domain for a URL.

        Arguments:
            url (string): The URL to parse.
            no_exception (boolean): Whether or not to throw an exception when the parse is unsuccessful.

        Returns:
            The domain for the provided URL.

        Raises:
            ValueError
        """
        if not UrlUtility.tlds:
            UrlUtility._populate_tlds()

        elements = urlparse(url)
        if elements[1] is None or len(elements[1]) == 0:
            elements = urlparse('//' + url)
        url_elements = elements[1].split('.')
        # url_elements = ["domain", "co", "uk"]

        for i in range(-len(url_elements), 0):
            last_i_elements = url_elements[i:]
            #    i=-3: ["domain", "co", "uk"]
            #    i=-2: ["co", "uk"]
            #    i=-1: ["uk"]

            candidate = ".".join(last_i_elements)  # domain.co.uk, co.uk, uk
            wildcard_candidate = ".".join(["*"] + last_i_elements[1:])  # *.co.uk, *.uk
            exception_candidate = "!" + candidate

            # match tlds
            if exception_candidate in UrlUtility.tlds:
                return ".".join(url_elements[i:])
            if candidate in UrlUtility.tlds or wildcard_candidate in UrlUtility.tlds:
                return ".".join(url_elements[i - 1:])
                # returns domain.co.uk

        if no_exception:
            return url
        else:
            msg = "Domain for URL=%s not in global list of TLDs" % url
            logger.error(msg)
            raise ValueError(msg)