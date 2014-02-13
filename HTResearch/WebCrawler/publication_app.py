from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy.utils.project import get_project_settings

from WebCrawler.utility_spiders import *
from WebCrawler.spiders import *
from HTResearch.Utilities.context import URLFrontierContext
from HTResearch.Utilities.logutil import get_logger, LoggingSection

if __name__ == '__main__':

#░░░░░░░░░▄░░░░░░░░░░░░░░▄
#░░░░░░░░▌▒█░░░░░░░░░░░▄▀▒▌
#░░░░░░░░▌▒▒█░░░░░░░░▄▀▒▒▒▐
#░░░░░░░▐▄▀▒▒▀▀▀▀▄▄▄▀▒▒▒▒▒▐
#░░░░░▄▄▀▒░▒▒▒▒▒▒▒▒▒█▒▒▄█▒▐
#░░░▄▀▒▒▒░░░▒▒▒░░░▒▒▒▀██▀▒▌
#░░▐▒▒▒▄▄▒▒▒▒░░░▒▒▒▒▒▒▒▀▄▒▒
#░░▌░░▌█▀▒▒▒▒▒▄▀█▄▒▒▒▒▒▒▒█▒
#░▐░░░▒▒▒▒▒▒▒▒▌██▀▒▒░░░▒▒▒▀ ▌
#░▌░▒▄██▄▒▒▒▒▒▒▒▒▒░░░░░░▒▒▒ ▌
#▀▒▀▐▄█▄█▌▄░▀▒▒░░░░░░░░░░▒▒ ▐
#▐▒▒▐▀▐▀▒░▄▄▒▄▒▒▒▒▒▒░▒░▒░▒▒ ▒▌
#▐▒▒▒▀▀▄▄▒▒▒▄▒▒▒▒▒▒▒▒░▒░▒░▒ ▐
#░▌▒▒▒▒▒▒▀▀▀▒▒▒▒▒▒░▒░▒░▒░▒▒ ▌
#░▐▒▒▒▒▒▒▒▒▒▒▒▒▒▒░▒░▒░▒▒▄▒▒
#░░▀▄▒▒▒▒▒▒▒▒▒▒▒░▒░▒░▒▄▒▒▒▒
#░░░░▀▄▒▒▒▒▒▒▒▒▒▒▄▄▄▀▒▒▒▒▄▀
#░░░░░░▀▄▄▄▄▄▄▀▀▀▒▒▒▒▒▄▄▀
#░░░░░░░░░▒▒▒▒▒▒▒▒▒▒
#such publication
    #very scrape
#wow
    #goggul skoler
    #wow

    logger = get_logger(LoggingSection.CRAWLER, 'app.py')
    logger.info("Starting a web crawl")

    spider = PublicationSpider()
    settings = get_project_settings()
    crawler = Crawler(settings)
    crawler.configure()
    crawler.crawl(spider)
    crawler.start()
    log.start()
    reactor.run()