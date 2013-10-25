from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy import log
from scrapy.utils.project import get_project_settings
from WebCrawler.spiders import *


spider = OrgSpider()
settings = get_project_settings()
crawler = Crawler(settings)
crawler.configure()
crawler.crawl(spider)
crawler.start()
log.start()
reactor.run()
