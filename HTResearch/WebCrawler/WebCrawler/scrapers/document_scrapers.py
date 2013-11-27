from ..items import *
from utility_scrapers import *


class ContactScraper():

    def parse(self, response):
        #get all the values out of the dictionary that the Contact scraper returns
        org_contact_scraper = OrgContactsScraper()
        contact_dicts = org_contact_scraper.parse(response)
        contacts = []
        for name in contact_dicts.iterkeys():
            contact = ScrapedContact()
            name_split = name.split()
            n = len(name_split)
            contact['first_name'] = ' '.join(name_split[0:n-1])
            contact['last_name'] = name_split[n-1]
            contact['primary_phone'] = contact_dicts[name]['number']
            contact['email'] = contact_dicts[name]['email']
            contact['position'] = contact_dicts[name]['position']
            contact['organization'] = contact_dicts[name]['organization']
            contacts.append(contact)
        return contacts



class OrganizationScraper():
    _scrapers = {
        'name': [OrgNameScraper()],
        'address': [OrgAddressScraper()],
        'types': [OrgTypeScraper()],
        'phone_number': [USPhoneNumberScraper(), IndianPhoneNumberScraper()],
        'email': [EmailScraper()],
        'contacts': [ContactNameScraper()],
        'organization_url': [OrgUrlScraper()],
        'partners': [OrgPartnersScraper()],
    }

    _multiple = ['types', 'phone_number', 'email', 'partners', 'contacts']

    def parse(self, response):
        organization = ScrapedOrganization()
        # Collect each field of organization model
        for field in self._scrapers.iterkeys():
            if field in self._multiple:
                # Get multiple field (e.g. phone_number)
                organization[field] = []
                for scraper in self._scrapers[field]:
                    organization[field] += scraper.parse(response)
            #elif field == 'contacts':
            #    organization[field] = scraper.pa
            else:
                # Get single field (e.g. name)
                results = self._scrapers[field][0].parse(response)
                if results:
                    organization[field] = results[0] if isinstance(results, type([])) else results
                else:
                    organization[field] = None
        return organization


class Publication:

    def __init__(self):
        publication = None