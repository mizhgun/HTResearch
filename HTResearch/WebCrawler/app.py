from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy import log
from scrapy.utils.project import get_project_settings
from WebCrawler.utility_spiders import DebugFileGenerator


# TODO: define spiders we want to use
spider = DebugFileGenerator(start_urls=["http://apneaap.org/about-us/our-board/"])
settings = get_project_settings()
crawler = Crawler(settings)
crawler.configure()
crawler.crawl(spider)
crawler.start()
log.start()
reactor.run()