# Library imports
from multiprocessing import Queue, Process, Condition, RLock, Value
from Queue import Empty, Full
from os import getpid

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
        self._qsize = Value('i', 0)
        self._urls = Queue(maxsize=self._max_size)
        self._jobs = Queue()
        self._factory = DAOFactory.get_instance(URLMetadataDAO)
        self._cache_cond = Condition()
        self._job_cond = Condition()
        self._cache_lock = RLock()
        self._cache_proc = Process(target=self._monitor_cache,
                                   args=(self._urls,
                                         self._jobs,
                                         self._job_cond,
                                         self._cache_cond,
                                         self._cache_lock))

    def start_cache_process(self):
        if not self._cache_proc.is_alive():
            self._cache_proc.start()

    def terminate_cache_process(self):
        if self._cache_proc.is_alive():
            self._cache_proc.terminate()

    def _monitor_cache(self, cache, job_queue, job_cond, cache_cond, cache_lock):
        while True:
            with job_cond:
                job_cond.wait()
                next_job = job_queue.get(block=False)

            if next_job == CacheJobs.Fill:
                with cache_cond:
                    urls = self._factory.findmany(self._max_size - cache.qsize(), "last_visited")
                    for u in urls:
                        url_obj = DTOConverter.from_dto(URLMetadata, u)
                        try:
                            cache.put(url_obj)
                        except Full:
                            break
                    cache_cond.notify_all()

            elif next_job == CacheJobs.Empty:
                with cache_lock:
                    while True:
                        try:
                            next_url = cache.get(block=False)
                            print next_url.url
                        except Empty:
                            break

    @property
    def next_url(self):
        with self._cache_lock:
            with self._cache_cond:
                try:
                    return self._urls.get(block=False)
                except Empty:
                    with self._job_cond:
                        self._jobs.put(CacheJobs.Fill)
                        self._job_cond.notify()
                    self._cache_cond.wait()
                    return self._urls.get(block=False)

    def put_url(self, u):
        with self._cache_lock:
            try:
                self._urls.put(u, block=False)
            except Full:
                pass
            url_dto = DTOConverter.to_dto(URLMetadataDTO, u)
            self._factory.create_update(url_dto)

    def empty_cache(self):
        with self._job_cond:
            self._jobs.put(CacheJobs.Empty)
            self._job_cond.notify()