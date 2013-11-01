from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy.utils.project import get_project_settings
from WebCrawler.spiders import *
from HTResearch.URLFrontier.urlfrontier import URLFrontier


if __name__ == '__main__':
    #"There exist limitless opportunities in every industry.
    #Where there is an open mind, there will always be a frontier."
    URLFrontier().start_cache_process()

    spider = OrgSpider()
    settings = get_project_settings()
    crawler = Crawler(settings)
    crawler.configure()
    crawler.crawl(spider)
    crawler.start()
    log.start()
    reactor.run()


