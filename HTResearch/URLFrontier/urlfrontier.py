# Library imports
import hashlib
from multiprocessing import Queue, Process, Condition, RLock, Manager, Array
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


class URLFrontierRules:
    def __init__(self, required_domains=[], blocked_domains=[], sort_list=["last_visited"]):
        self._required_domains = required_domains
        self._blocked_domains = blocked_domains
        self._sort_list = sort_list
        self.checksum = self._generate_checksum()

    @property
    def checksum(self):
        return self.checksum

    def _generate_checksum(self):
        md5 = hashlib.md5()
        for dom in self._required_domains:
            md5.update("req" + dom)
        for dom in self._blocked_domains:
            md5.update("block" + dom)
        for sort in self._sort_list:
            md5.update("sort" + sort)
        return md5.hexdigest()


class URLFrontier:
    __metaclass__ = Singleton

    def __init__(self):
        self._max_size = 1000
        self._factory = DAOFactory.get_instance(URLMetadataDAO)
        self._start_term_lock = RLock()
        self._url_queues = dict()
        self._job_queues = dict()
        self._next_url_locks = dict()
        self._fill_conds = dict()
        self._empty_conds = dict()
        self._job_conds = dict()
        self._cache_procs = dict()
        self._proc_counts = dict()

    def start_cache_process(self, rules=URLFrontierRules()):
        with self._start_term_lock:
            cs = rules.checksum
            if cs not in self._cache_procs.keys():
                self._url_queues[cs] = Queue(maxsize=self._max_size)
                self._job_queues[cs] = Queue()
                self._next_url_locks[cs] = RLock()
                self._fill_conds[cs] = Condition()
                self._empty_conds[cs] = Condition()
                self._job_conds[cs] = Condition()
                self._cache_procs[cs] = Process(target=self._monitor_cache,
                                                args=(self._url_queues[cs],
                                                      self._job_queues[cs],
                                                      self._job_conds[cs],
                                                      self._fill_conds[cs],
                                                      self._empty_conds[cs]))
                self._proc_counts[cs] = 0
            if not self._cache_procs[cs].is_alive():
                self._cache_procs[cs].start()
            self._proc_counts[cs] += 1

    def terminate_cache_process(self, rules=URLFrontierRules()):
        with self._start_term_lock:
            cs = rules.checksum
            if cs not in self._proc_counts.keys():
                return

            self._proc_counts[cs] -= 1
            if self._proc_counts[cs] <= 0:
                if self._cache_procs[cs].is_alive():
                    self._cache_procs[cs].terminate()
                del self._cache_procs[cs]
                del self._url_queues[cs]
                del self._job_queues[cs]
                del self._next_url_locks[cs]
                del self._fill_conds[cs]
                del self._empty_conds[cs]
                del self._job_conds[cs]

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

    def next_url(self, rules=URLFrontierRules()):
        cs = rules.checksum
        start_process = False

        with self._start_term_lock:
            if cs not in self._cache_procs.keys():
                start_process = True
        if start_process:
            start_process(rules=rules)

        with self._next_url_locks[cs]:
            with self._empty_conds[cs]:
                try:
                    return self._url_queues[cs].get(block=False)
                except Empty:
                    with self._fill_conds[cs]:
                        with self._job_conds[cs]:
                            self._job_queues[cs].put(CacheJobs.Fill)
                            self._job_conds[cs].notify()
                        self._fill_conds[cs].wait()
                    if not self._url_queues[cs].empty():
                        return self._url_queues[cs].get(block=False)
                    else:
                        return None

    def put_url(self, u):
        url_dto = DTOConverter.to_dto(URLMetadataDTO, u)
        self._factory.create_update(url_dto)

    def empty_cache(self, rules=URLFrontierRules()):
        cs = rules.checksum
        with self._job_conds[cs]:
            self._job_queues[cs].put(CacheJobs.Empty)
            self._job_conds[cs].notify()
        with self._empty_conds[cs]:
            if not self._url_queues[cs].empty():
                self._empty_conds[cs].wait()
