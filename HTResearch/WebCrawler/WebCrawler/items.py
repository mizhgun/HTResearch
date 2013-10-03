# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class ScrapedUrl(Item):
    # define the fields for your item here like:
    # name = Field()
    url = Field()

class ScrapedEmail(Item):
    email = Field()

class ScrapedOrganization(Item):
    name = Field()
    address = Field()
    types = Field()
    phone_number = Field()
    email_address = Field()
    contacts = Field()
    organization_url = Field()
    partners = Field()

class ScrapedPhoneNumber(Item):
    phone_number=Field()
