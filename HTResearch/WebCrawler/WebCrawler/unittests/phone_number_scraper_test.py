from scrapy.spider import BaseSpider
from ..scrapers.utility_scrapers import USPhoneNumberScraper, IndianPhoneNumberScraper
from ..items import ScrapedPhoneNumber
import os

class PhoneNumberScraperTest(BaseSpider):
    name = "phone_number_scraper_test"
    start_urls = ["http://www.stoptrafficking.in/Directory.aspx"]
    scraper = None

    def __init__(self, *args, **kwargs):
        self.saved_path = os.getcwd()
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        super(PhoneNumberScraperTest, self).__init__(*args, **kwargs)
        self.scraper = IndianPhoneNumberScraper()
        if not os.path.exists("../Output/"):
            os.makedirs("../Output")
        else:
            try:
                os.remove("../Output/phone_number_scraper_output.txt")
            except OSError:
                pass

    def __del__(self):
        os.chdir(self.saved_path)

    def parse(self, response):
        numbers = self.scraper.parse(response)

        with open("../Output/phone_number_scraper_output.txt", 'a') as f:
            for number in numbers:
                f.write(number["phone_number"] + "\n")
                print(number["phone_number"])
        return numbers
