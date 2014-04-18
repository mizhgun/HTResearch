class MockContactNameScraper(object):

    def parse(self, response):
        return ['test']


class MockEmailScraper(object):

    def parse(self, response):
        return ['test']


class MockIndianPhoneNumberScraper(object):

    def parse(self, response):
        return ['test']


class MockKeywordScraper(object):

    def parse(self, response):
        keyword_lookup = {
            "http://bombayteenchallenge.org/":
                "bombay challenge teen seek mumbai education woman health india life music read rescued street "
                "vocational program  blog btc care child contact district donate drug gift light live men office reach "
                "red safe tel training trust wa addict 501c3 access afraid allows ambedkar announced ash bandra beauty "
                "began betrayed bound",
            "http://www.nsa.gov/":
                "nsa national security cryptologic flash news intelligence mission agency anniversary business menu "
                "nsacss partnership top transcript video view statement area awareness center core cyber cybersecurity "
                "director intro latest life month museum nation oct office opportunity oversight player signal skip "
                "authority 10th 20th 60th accessibility acquisition adobe alexander announces assurance",
            "http://www.halftheskymovement.org/":
                "view issue campaign maternal mortality sex trafficking forced prostitution economic empowerment "
                "education genderbased violence partner solution film game ambassador donate facebook featured half "
                "movement ngo screening sky tool video woman action adan additional advocate america amie basu blog "
                "book broadcast buy campus celebritiesadvocates community contact diane edna eva ferrera find",
        }
        return keyword_lookup[response.url]


class MockOrgAddressScraper(object):

    def parse(self, response):
        return 'test'


class MockOrgContactsScraper(object):

    def parse(self, response):
        return {'test test': {
                'number': ['test'],
                'email': 'test',
                'position': 'test',
                'organization': 'test',
                }
                }


class MockOrgFacebookScraper(object):

    def parse(self, response):
        return 'test'


class MockOrgTwitterScraper(object):

    def parse(self, response):
        return 'test'


class MockOrgNameScraper(object):

    def parse(self, response):
        return 'test'


class MockOrgPartnersScraper(object):

    def parse(self, response):
        return ['test']


class MockOrgTypeScraper(object):

    def parse(self, response):
        return ['test']


class MockOrgUrlScraper(object):

    def parse(self, response):
        return response.url


class MockPublicationAuthorsScraper(object):

    def parse(self, response):
        return ['test']


class MockPublicationDateScraper(object):

    def parse(self, response):
        return 'test'


class MockPublicationPublisherScraper(object):

    def parse(self, response):
        return 'test'


class MockPublicationTitleScraper(object):

    def parse(self, response):
        return 'test'


class MockPublicationTypeScraper(object):

    def parse(self, response):
        return 'test'


class MockUrlMetadataScraper(object):

    def parse(self, response):
        return 'test'


class MockUSPhoneNumberScraper(object):

    def parse(self, response):
        return ['test']
