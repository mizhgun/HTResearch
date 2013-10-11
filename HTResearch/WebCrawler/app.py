from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy import log
from scrapy.utils.project import get_project_settings
from WebCrawler.unittests.phone_number_scraper_test import PhoneNumberScraperTest
from WebCrawler.unittests.keyword_scraper_test import KeywordScraperTest


# TODO: define spiders we want to use
spider = PhoneNumberScraperTest()
settings = get_project_settings()
crawler = Crawler(settings)
crawler.configure()
crawler.crawl(spider)
crawler.start()
log.start()
reactor.run()