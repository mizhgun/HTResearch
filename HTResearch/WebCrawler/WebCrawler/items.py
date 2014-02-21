# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class ScrapedAddress(Item):
    city = Field()
    zip_code = Field()


class ScrapedContact(Item):
    first_name = Field()
    last_name = Field()
    phones = Field()
    email = Field()
    organization = Field()
    publications = Field()
    position = Field()


class ScrapedContactName(Item):
    name = Field()


class ScrapedEmail(Item):
    email = Field()


class ScrapedOrgName(Item):
    name = Field()


class ScrapedOrganization(Item):
    name = Field()
    address = Field()
    types = Field()
    phone_numbers = Field()
    emails = Field()
    contacts = Field()
    organization_url = Field()
    partners = Field()
    facebook = Field()
    twitter = Field()
    keywords = Field()
    page_rank_info = Field()


class ScrapedPhoneNumber(Item):
    phone_number = Field()


class ScrapedPublication(Item):
    title = Field()
    authors = Field()
    publisher = Field()
    publication_date = Field()
    types = Field()
    content_url = Field()


class ScrapedUrl(Item):
    url = Field()
    domain = Field()
    last_visited = Field()
    score = Field()
    update_freq = Field()
    checksum = Field()
