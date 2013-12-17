from datetime import datetime
from scrapy.http import Request
from springpython.context import ApplicationContext

from HTResearch.DataAccess.dao import URLMetadataDAO
from HTResearch.Utilities.context import URLFrontierContext
from HTResearch.Utilities.logutil import *

_middleware_logger = get_logger(LoggingSection.CRAWLER, __name__)


class UrlQueueMiddleware(object):

    def process_exception(self, request, exception, spider):
        """
        An exception occurred while trying to get a response from the requested URL,
        so we need to do cleanup. This means updating the URLMetadata to reflect that
        this URL has been checked and queuing a new URL request from the URLFrontier.
        """

        # log error
        _middleware_logger.error(exception.message)

        # update last_visited for failed request
        try:
            url_dao = URLMetadataDAO()
            url_dto = url_dao.find(url=request.url)
            if url_dto is not None:
                url_dto.last_visited = datetime.utcnow()
                url_dao.create_update(url_dto)
        except Exception as e:
            _middleware_logger.error(e.message)

        # queue next url
        ctx = ApplicationContext(URLFrontierContext())
        url_frontier = ctx.get_object("URLFrontier")
        try:
            url_frontier_rules = spider.url_frontier_rules
        except Exception as e:
            _middleware_logger.error('ERROR: Spider without url_frontier_rules defined')
            return None

        next_url = url_frontier.next_url(url_frontier_rules)
        if next_url is not None:
            return Request(next_url.url, dont_filter=True)
        return None
