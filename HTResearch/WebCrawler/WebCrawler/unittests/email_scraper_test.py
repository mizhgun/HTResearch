from scrapy.spider import BaseSpider
from HTResearch.WebCrawler.WebCrawler.scrapers.utility_scrapers import EmailScraper


class EmailScraperTest(BaseSpider):
    name = "email_scraper_test"
    start_urls = ["http://nhrc.nic.in/ContactUs.htm",
                  "https://bombayteenchallenge.org/"]

    def __init__(self, *args, **kwargs):
        super(EmailScraperTest, self).__init__(*args, **kwargs)
        self.scraper = EmailScraper()

    def parse(self, response):
        emails = self.scraper.parse(response)
        
        for element in emails:
            print(element["email"])

        return emails
