from multiprocessing import Queue, Process
from HTResearch.DataModel.model import URLMetadata
from HTResearch.DataModel.converter import DTOConverter
from HTResearch.DataAccess.dao import URLMetadataDAO
from HTResearch.DataAccess.dto import URLMetadataDTO
from HTResearch.DataAccess.factory import DAOFactory


class URLFrontier(object):

    def __init__(self):
        self._urls = Queue(maxsize=1000)
        self._factory = DAOFactory.get_instance(URLMetadataDAO)
        self._cache_process = Process(target=self._monitor_cache, args=(self._urls,))

    def __enter__(self):
        self._cache_process.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cache_process.terminate()

    def _monitor_cache(self, queue):
        while True:
            if queue.empty():
                urls = self._factory.findmany(1000, "last_visited")
                for u in urls:
                    queue.put(u)

    @property
    def next_url(self):
        while self._urls.empty():
            pass
        return self._urls.get()

    @property
    def empty(self):
        return self._urls.empty()

    def put_url(self, url):
        if not self._urls.full():
            self._urls.put(url)
        url_obj = URLMetadata(url=url)
        url_dto = DTOConverter.to_dto(URLMetadataDTO, url_obj)
        self._factory.create_update(url_dto)