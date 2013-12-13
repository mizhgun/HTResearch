from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy.utils.project import get_project_settings
from springpython.context import ApplicationContext

from WebCrawler.spiders import *
from HTResearch.Utilities.context import URLFrontierContext
from HTResearch.Utilities.logutil import get_logger, LoggingSection

if __name__ == '__main__':

 #             _,----'  _______________________  `----._
 #          ,-'  __,---'  ___________________  `---.__  `-.
 #       ,-'  ,-'  __,---'  _______________  `---.__  `-.  `-.
 #     ,'  ,-'  ,-'  __,---'                `---.__  `-.  `-.  `.
 #    /  ,'  ,-'  ,-'                               `-.  `-.  `.  \
 #   / ,'  ,' ,--'     "There exist limitless          `--. `.  `. \
 #  | /  ,' ,'    opportunities in every industry.         `. `.  \ |
 # ,--. ,--.         Where there is an open mind,             _______
 #( `  "   ')     there will always be a frontier."          (_______)
 # >-  .  -<                                                 /       \
 #( ,      .)                                               ( G O L D )
 # `--'^`--'               Paul Poulsen                      \_______/
 #    /_\


    logger = get_logger(LoggingSection.CRAWLER, 'app.py')
    logger.info("Starting a web crawl")

    ctx = ApplicationContext(URLFrontierContext())
    frontier = ctx.get_object("URLFrontier")
    frontier.start_cache_process()

    spider = OrgSpider()
    settings = get_project_settings()
    crawler = Crawler(settings)
    crawler.configure()
    crawler.crawl(spider)
    crawler.start()
    log.start()
    reactor.run()