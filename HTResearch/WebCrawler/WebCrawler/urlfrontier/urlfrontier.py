from Queue import Queue
from Queue import Empty
from Queue import Full
from HTResearch.DataModel.model import URLMetadata
from HTResearch.DataModel.converter import DTOConverter
from HTResearch.DataAccess.dao import URLMetadataDAO
from HTResearch.DataAccess.dto import URLMetadataDTO
from HTResearch.DataAccess.factory import DAOFactory


class URLFrontier(object):

    def __init__(self):
        self.urls = Queue(maxsize=1000)
        self.factory = DAOFactory.get_instance(URLMetadataDAO)
        self._populate()

    def push_url(self, url):
        try:
            self.urls.put(url)
        except Full:
            url_obj = URLMetadata(url=url)
            url_dto = DTOConverter.to_dto(URLMetadataDTO, url_obj)
            self.factory.create_update(url_dto)

    def pop_url(self):
        try:
            return self.urls.get()
        except Empty:
            self._populate()
            return self.urls.get()

    def _populate(self):
        urls = self.factory.findmany(1000, "last_visited")

        [self.urls.put(u) for u in urls]