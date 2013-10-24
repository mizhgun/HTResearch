from scrapy.spider import BaseSpider
#from scrapy import log
from ..scrapers.utility_scrapers import ContactNameScraper
import pdb
import os


class ContactScraperTest(BaseSpider):
    name = "contact_name_scraper_test"
    #start_urls = ["http://www.prajwalaindia.com/contactus.html",
    #              "http://www.ijm.org/who-we-are/leadership",
    #              "http://www.tiss.edu/lefttop/faculty-staff/Administrators",
    #              "http://www.bba.org.in/?q=content/team",
    #              "http://apneaap.org/about-us/our-board/" ]
    start_urls = ["http://apneaap.org/about-us/our-board/"]
    #start_urls = ["http://www.prajwalaindia.com/contactus.html"]

    def __init__(self, *args, **kwargs):
        self.saved_path = os.getcwd()
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        super(ContactScraperTest, self).__init__(*args, **kwargs)
        self.scraper = ContactNameScraper()
        if not os.path.exists("../Output/"):
            os.makedirs("../Output")
        else:
            try:
                os.remove("../Output/contact_name_scraper_output.txt")
            except OSError:
                pass

    def __del__(self):
        os.chdir(self.saved_path)

    def parse(self, response):
        names = self.scraper.parse(response)
        with open("../Output/contact_name_scraper_output.txt", 'a') as f:
            for element in names:
                f.write(element['name'] + "\n")
                print(element['name'])

        return names