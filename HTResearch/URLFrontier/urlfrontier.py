# Library imports
from multiprocessing import Queue, Process
from Queue import Empty, Full

# Project imports
from HTResearch.DataModel.model import URLMetadata
from HTResearch.DataModel.converter import DTOConverter
from HTResearch.DataAccess.dao import URLMetadataDAO
from HTResearch.DataAccess.dto import URLMetadataDTO
from HTResearch.DataAccess.factory import DAOFactory
from HTResearch.Utilities.types import Singleton


class CacheJobs():
    Fill, Empty = range(2)


class URLFrontier:
    __metaclass__ = Singleton

    def __init__(self):
        self._max_size = 1000
        self._urls = Queue(maxsize=self._max_size)
        self._jobs = Queue()
        self._jobs.put(CacheJobs.Fill)
        self._factory = DAOFactory.get_instance(URLMetadataDAO)
        self._cache_proc = Process(target=self._monitor_cache, args=(self._urls, self._jobs))

    def start_cache_process(self):
        if not self._cache_proc.is_alive():
            self._cache_proc.start()

    def terminate_cache_process(self):
        if self._cache_proc.is_alive():
            self._cache_proc.terminate()

    def _monitor_cache(self, url_queue, job_queue):
        while True:
            try:
                next_job = job_queue.get(block=False)
            except Empty:
                continue

            if next_job == CacheJobs.Fill:
                urls = self._factory.findmany(1000, "last_visited")
                for u in urls:
                    url_obj = DTOConverter.from_dto(URLMetadata, u)
                    url_queue.put(url_obj)
            elif next_job == CacheJobs.Empty:
                while True:
                    try:
                        self._urls.get(block=False)
                    except Empty:
                        break

    @property
    def next_url(self):
        while True:
            try:
                return self._urls.get(block=False)
            except Empty:
                self._jobs.put(CacheJobs.Fill)

    def put_url(self, u):
        try:
            self._urls.put(u, block=False)
        except Full:
            pass
        url_dto = DTOConverter.to_dto(URLMetadataDTO, u)
        self._factory.create_update(url_dto)

    def empty_cache(self):
        self._jobs.put(CacheJobs.Empty)