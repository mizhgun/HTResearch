from HTResearch.WebCrawler.WebCrawler.items import *


class MockContactNameScraper:
    def parse(self, response):
        return []


class MockContactPositionScraper:
    def parse(self, response):
        return ''


class MockContactPublicationsScraper:
    def parse(self, response):
        return []


class MockEmailScraper(object):
    def parse(self, response):
        return []


class MockIndianPhoneNumberScraper(object):
    def parse(self, response):
        return []


class MockKeywordScraper(object):
    def parse(self, response):
        return ''


class MockOrgAddressScraper(object):
    def parse(self, response):
        return ''


class MockOrgContactsScraper(object):
    def parse(self, response):
        return []


class MockOrgFacebookScraper(object):
    def parse(self, response):
        return ''


class MockOrgTwitterScraper(object):
    def parse(self, response):
        return ''


class MockOrgNameScraper(object):
    def parse(self, response):
        return ''


class MockOrgPartnersScraper(object):
    def parse(self, response):
        return []


class MockOrgTypeScraper(object):
    def parse(self, response):
        return []


class MockOrgUrlScraper(object):
    def parse(self, response):
        return []


class MockPublicationAuthorsScraper:
    def parse(self, response):
        return []


class MockPublicationDateScraper:
    def parse(self, response):
        return []


class MockPublicationPublisherScraper:
    def parse(self, response):
        return []


class MockPublicationTitleScraper:
    def parse(self, response):
        return []


class MockPublicationTypeScraper:
    def parse(self, response):
        return []


class MockUrlMetadataScraper(object):
    def parse(self, response):
        return ScrapedUrl()


class MockUSPhoneNumberScraper(object):
    def parse(self, response):
        return []
