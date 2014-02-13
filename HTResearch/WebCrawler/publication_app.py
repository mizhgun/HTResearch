#!-*- coding: utf-8 -*-
from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy.utils.project import get_project_settings
from WebCrawler.spiders import *
from HTResearch.Utilities.logutil import get_logger, LoggingSection

if __name__ == '__main__':

#wow
    #many piethon
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
#goggul skoler
    #wow

    query = raw_input("Please enter search query for Publication Scraper: ")
    num_pages = raw_input("How many pages would you like to scrape?: ")
    num_pages = int(num_pages)

    #I have to use this workflow because Scrapy breaks the workflow with DFS and BFS
    query = query.replace(' ', '+')
    urls = ['http://scholar.google.com/scholar?q=' + query + '&hl=en']

    for i in range(1, num_pages):
        urls.append('http://scholar.google.com/scholar?start='+str(i*10)+'&q=' + query + '&hl=en')

    for url in urls:
        logger = get_logger(LoggingSection.CRAWLER, 'publication_app.py')
        logger.info("Starting a web crawl")
        spider = PublicationSpider()
        settings = get_project_settings()
        crawler = Crawler(settings)
        crawler.configure()
        crawler.crawl(spider)
        crawler.start()
        log.start()
        reactor.run()
