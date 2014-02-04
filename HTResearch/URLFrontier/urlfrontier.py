# Library imports
import hashlib
# stdlib imports
from multiprocessing import Queue, Process, Condition, RLock
from Queue import Empty, Full

# project imports
from HTResearch.DataAccess.dto import URLMetadataDTO
from HTResearch.DataModel.model import URLMetadata
from HTResearch.Utilities.converter import DTOConverter
from HTResearch.Utilities.types import Singleton
from HTResearch.Utilities.logutil import LoggingSection, get_logger


logger = get_logger(LoggingSection.FRONTIER, __name__)


class CacheJobs():
    Fill, Empty = range(2)


class URLFrontierRules:
    def __init__(self, required_domains=[], blocked_domains=[], sort_list=["last_visited"]):
        self._required_domains = required_domains
        self._blocked_domains = blocked_domains
        self._sort_list = sort_list
        self._checksum = self._generate_checksum()

    @property
    def checksum(self):
        return self._checksum

    @property
    def required_domains(self):
        return self._required_domains

    @property
    def blocked_domains(self):
        return self._blocked_domains

    @property
    def sort_list(self):
        return ",".join(self._sort_list)

    def _generate_checksum(self):
        md5 = hashlib.md5()
        for dom in self._required_domains:
            md5.update("req" + dom)
        for dom in self._blocked_domains:
            md5.update("block" + dom)
        for sort in self._sort_list:
            md5.update("sort" + sort)
        return md5.hexdigest()


def _monitor_cache(dao, max_size, cache, job_queue, job_cond, fill_cond, empty_cond,
                   req_doms, blk_doms, srt_list, logger_lock):
    while True:
        try:
            with job_cond:
                next_job = job_queue.get(block=False)
        except Empty:
            with job_cond:
                job_cond.wait(1)
                try:
                    next_job = job_queue.get(block=False)
                except Empty:
                    continue

        if next_job == CacheJobs.Fill:
            with logger_lock:
                logger.info('Filling the cache')
            with fill_cond:
                urls = dao().findmany_by_domains(max_size - cache.qsize(),
                                                 req_doms, blk_doms, srt_list)
                for u in urls:
                    url_obj = DTOConverter.from_dto(URLMetadata, u)
                    try:
                        cache.put(url_obj)
                    except Full:
                        break
                fill_cond.notify_all()

        elif next_job == CacheJobs.Empty:
            with logger_lock:
                logger.info('Emptying the cache')
            with empty_cond:
                while True:
                    try:
                        cache.get(block=False)
                    except Empty:
                        break
                empty_cond.notify()


class URLFrontier:
    __metaclass__ = Singleton

    def __init__(self):
        # Injected dependencies
        self.dao = None

        # Private members
        self._max_size = 1000
        self._start_term_lock = RLock()
        self._url_queues = dict()
        self._job_queues = dict()
        self._next_url_locks = dict()
        self._fill_conds = dict()
        self._empty_conds = dict()
        self._mid_empty_conds = dict()
        self._job_conds = dict()
        self._cache_procs = dict()
        self._proc_counts = dict()
        self._logger_lock = RLock()

    def start_cache_process(self, rules=URLFrontierRules()):
        with self._start_term_lock:
            cs = rules.checksum
            if cs not in self._cache_procs.keys():
                self._url_queues[cs] = Queue(maxsize=self._max_size)
                self._job_queues[cs] = Queue()
                self._next_url_locks[cs] = RLock()
                self._fill_conds[cs] = Condition()
                self._empty_conds[cs] = Condition()
                self._mid_empty_conds[cs] = Condition()
                self._job_conds[cs] = Condition()
                self._cache_procs[cs] = Process(target=_monitor_cache,
                                                args=(self.dao,
                                                      self._max_size,
                                                      self._url_queues[cs],
                                                      self._job_queues[cs],
                                                      self._job_conds[cs],
                                                      self._fill_conds[cs],
                                                      self._empty_conds[cs],
                                                      rules.required_domains,
                                                      rules.blocked_domains,
                                                      rules.sort_list,
                                                      self._logger_lock))
                self._proc_counts[cs] = 0
            if not self._cache_procs[cs].is_alive():
                with self._logger_lock:
                    logger.info('Starting the cache process for rule=%s' % cs)
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
                    with self._logger_lock:
                        logger.info('Stopping the cache process for rule %s' % cs)
                    self._cache_procs[cs].terminate()
                del self._cache_procs[cs]
                del self._url_queues[cs]
                del self._job_queues[cs]
                del self._next_url_locks[cs]
                del self._fill_conds[cs]
                del self._empty_conds[cs]
                del self._job_conds[cs]

    def next_url(self, rules=URLFrontierRules()):
        cs = rules.checksum
        start_process = False

        with self._start_term_lock:
            if cs not in self._cache_procs.keys():
                start_process = True
        if start_process:
            self.start_cache_process(rules=rules)

        with self._next_url_locks[cs]:
            with self._mid_empty_conds[cs]:
                try:
                    return self._url_queues[cs].get(block=False)
                except Empty:
                    with self._fill_conds[cs]:
                        with self._job_conds[cs]:
                            self._job_queues[cs].put(CacheJobs.Fill)
                            self._job_conds[cs].notify()
                        self._fill_conds[cs].wait()
                    try:
                        return self._url_queues[cs].get(block=False)
                    except Empty:
                        return None

    def put_url(self, u):
        url_dto = DTOConverter.to_dto(URLMetadataDTO, u)
        self.dao().create_update(url_dto)

    def empty_cache(self, rules=URLFrontierRules()):
        cs = rules.checksum
        with self._mid_empty_conds[cs]:
            with self._empty_conds[cs]:
                repeat = True
                while repeat:
                    with self._job_conds[cs]:
                        self._job_queues[cs].put(CacheJobs.Empty)
                        self._job_conds[cs].notify()
                    try:
                        timeout = 10
                        while not self._url_queues[cs].empty() and timeout:
                            self._empty_conds[cs].wait(1)
                            timeout -= 1
                        self._url_queues.get(block=False)
                    except Exception as e:
                        repeat = False
