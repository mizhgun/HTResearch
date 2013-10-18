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
        self._urls = Queue(maxsize=1000)
        self._factory = DAOFactory.get_instance(URLMetadataDAO)
        self._size = 0
        self._populate()

    def __len__(self):
        return self._size

    @property
    def next_url(self):
        try:
            return self._urls.get()
        except Empty:
            self._populate()
            return self._urls.get()
        finally:
            self._size -= 1

    def put_url(self, url):
        try:
            self._urls.put(url)
            self._size += 1
        except Full:
            url_obj = URLMetadata(url=url)
            url_dto = DTOConverter.to_dto(URLMetadataDTO, url_obj)
            self._factory.create_update(url_dto)

    def _populate(self):
        urls = self._factory.findmany(1000, "last_visited")

        for u in urls:
            self._urls.put(u)
            self._size += 1