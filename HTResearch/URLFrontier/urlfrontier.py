# Library imports
from multiprocessing import Queue, Process, Condition, RLock
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
        self._factory = DAOFactory.get_instance(URLMetadataDAO)
        self._next_url_lock = RLock()
        self._fill_cond = Condition()
        self._empty_cond = Condition()
        self._job_cond = Condition()
        self._cache_proc = Process(target=self._monitor_cache,
                                   args=(self._urls,
                                         self._jobs,
                                         self._job_cond,
                                         self._fill_cond,
                                         self._empty_cond))

    def start_cache_process(self):
        if not self._cache_proc.is_alive():
            self._cache_proc.start()

    def terminate_cache_process(self):
        if self._cache_proc.is_alive():
            self._cache_proc.terminate()

    def _monitor_cache(self, cache, job_queue, job_cond, fill_cond, empty_cond):
        while True:
            try:
                next_job = job_queue.get(block=False)
            except Empty:
                with job_cond:
                    job_cond.wait()
                    next_job = job_queue.get(block=False)

            if next_job == CacheJobs.Fill:
                with fill_cond:
                    urls = self._factory.findmany(self._max_size - cache.qsize(), "last_visited")
                    for u in urls:
                        url_obj = DTOConverter.from_dto(URLMetadata, u)
                        try:
                            cache.put(url_obj)
                        except Full:
                            break
                    fill_cond.notify_all()

            elif next_job == CacheJobs.Empty:
                with empty_cond:
                    while True:
                        try:
                            cache.get(block=False)
                        except Empty:
                            empty_cond.notify()
                            break

    @property
    def next_url(self):
        with self._next_url_lock:
            with self._empty_cond:
                try:
                    return self._urls.get(block=False)
                except Empty:
                    with self._fill_cond:
                        with self._job_cond:
                            self._jobs.put(CacheJobs.Fill)
                            self._job_cond.notify()
                        self._fill_cond.wait()
                    if not self._urls.empty():
                        return self._urls.get(block=False)
                    else:
                        return None

    def put_url(self, u):
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
        with self._empty_cond:
            if not self._urls.empty():
                self._empty_cond.wait()
