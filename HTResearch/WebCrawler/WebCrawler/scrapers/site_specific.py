import re
import string
from urlparse import urlparse

from scrapy.http import TextResponse
from scrapy.selector import HtmlXPathSelector

from HTResearch.WebCrawler.WebCrawler.scrapers.utility_scrapers import USPhoneNumberScraper, IndianPhoneNumberScraper

from ..items import ScrapedOrganization, ScrapedContact


class StopTraffickingDotInScraper:
    """An ad hoc scraper for the page: http://www.stoptrafficking.in/Directory.aspx"""

    # parses the onclick attribute for the cid we will use to find the popup windows
    # use first .group(1) to get the cid out
    onclick_re = re.compile(r"^javascript:window\.open\('ServicesPopup\.aspx\?cid=(\d+)',.*$")

    # constructors
    def __init__(self):
        pass

    def parse_directory(self, response):
        """Scrape the HttpRequest.Response of the Directory.aspx page for Orgs/Contacts"""

        # Reference regex so I only have to type this once
        regex = StopTraffickingDotInScraper.onclick_re

        # Create XPath selector
        if isinstance(response, TextResponse):
            hxs = HtmlXPathSelector(response)
        
            # get our data from the gvFaq table
            table = hxs.select('//table[@id="gvFaq"]')
            # first row is headers, so grab everything after
            rows = table.select('tr[position() > 1]')

            # collect values from each column
            states = rows.select('td[1]/font/text()').extract()
            districts = rows.select('td[2]/font/text()').extract()
            orgnames = rows.select('td[3]/font/a/text()').extract()
            onclicks = rows.select('td[3]/font/a/@onclick').extract()
            categories = rows.select('td[4]/font/text()').extract()
            contacts = rows.select('td[5]/font/text()').extract()
            contact_numbers = rows.select('td[6]/font/text()').extract()

            #extract cids from onclicks
            cids = []
            for onclick in onclicks:
                cids.append(regex.match(onclick).group(1))

            #Create _TableDate items to store data for parsing popups
            items = self._create_items(states, districts, orgnames, categories, contacts, contact_numbers, cids)

        return items 

    def parse_popup(self, response, table_entry):
        """Parse a Popup from StopTrafficking.in (and integrate with table data)"""

        hxs = HtmlXPathSelector(response)

        # get our data from the cells
        cells = hxs.select('//table/tr/td')

        # Extract data to popup dictionary
        popup = {}
        popup['org'] = cells.select('span[@id ="lblOrgName"]/text()').extract()
        popup['category'] = cells.select('span[@id ="lblCategory"]/text()').extract()
        popup['contact_name'] = cells.select('span[@id ="lblContactName"]/text()').extract()
        popup['serv_area'] = cells.select('span[@id ="lblServiceArea"]/text()').extract()
        popup['interests'] = cells.select('span[@id ="lblInvolve"]/text()').extract()
        popup['address'] = cells.select('span[@id ="lblAddress"]/text()').extract()
        popup['state'] = cells.select('span[@id ="lblState"]/text()').extract()
        popup['district'] = cells.select('span[@id ="lblDistrict"]/text()').extract()
        popup['url'] = cells.select('span[@id ="lblURL"]/text()').extract()
        popup['telephone'] = cells.select('span[@id ="lblTelephone"]/text()').extract()
        popup['email1'] = cells.select('span[@id ="lblEmail"]/text()').extract()
        popup['email2'] = cells.select('span[@id ="lblEmail2"]/text()').extract()
        popup['mobile1'] = cells.select('span[@id ="lblMobile1"]/text()').extract()
        popup['mobile2'] = cells.select('span[@id ="lblMobile2"]/text()').extract()

        # turn lists into single variables
        keys = popup.keys()
        for key in keys:
            if popup[key]: popup[key] = popup[key][0]
            else: popup[key] = None

        # Turn comma-separated values to lists, alter names, etc.
        popup = self.parse_popup_fields(popup, table_entry)

        items = None
        if popup['category'] == 'Individual' or popup['category'] == 'Nodal Police Officer':
            items = self._create_contact(popup)
        else:
            items = self._create_org(popup)

        return items

    def parse_popup_fields(self, popup, table_entry):
        popup['org'] = self._edit_org(popup['org'], popup)
        popup['category'] = self._edit_category(popup['category'])
        popup['contact_name'] = self._edit_contact_name(popup['contact_name'], popup)
        popup['serv_area'] = self._edit_serv_area(popup['serv_area'])
        popup['interests'] = self._edit_interests(popup['interests'])
        popup['address'] = self._edit_address(popup['address'])
        popup['state'] = self._edit_state(popup['state'])
        popup['district'] = self._edit_district(popup['district'])
        popup['url'] = self._edit_url(popup['url'])
        popup['telephone'] = self._edit_phone(popup['telephone'])
        popup['email1'] = self._edit_email(popup['email1'])
        popup['email2'] = self._edit_email(popup['email2'])
        popup['mobile1'] = self._edit_phone(popup['mobile1'])
        popup['mobile2'] = self._edit_phone(popup['mobile2'])

        return popup

    def _create_contact(self, popup):
        """Take an inputed popup dictionary and return ScrapedContact"""

        #Convert names to first and last name
        names = self._parse_contact_name(popup['contact_name'])
        first = names[0]
        last = names[1]

        # combine phone numbers, first will be primary and 2nd secondary
        telephone = popup['telephone'] if popup['telephone'] is not None else []
        mobile1 = popup['mobile1'] if popup['mobile1'] is not None else []
        mobile2 = popup['mobile2'] if popup['mobile2'] is not None else []
        numbers = telephone + mobile1 + mobile2
        primary_no = None
        sec_no = None
        if len(numbers) > 0:
            primary_no = numbers[0]
        if len(numbers) > 1:
            sec_no = numbers[1]

        # grab email
        email = None
        if popup['email1']:
            email = popup['email1'][0]

        #grab position
        position = None
        if 'role' in popup.keys():
            position = popup['role']

        #create contact
        contact = ScrapedContact(
            first_name = first,
            last_name = last,
            primary_phone= primary_no,
            secondary_phone = sec_no, 
            email = email,
            organization = None,
            publications = None,
            position = '') 
        return contact

    def _create_org(self, popup):
        # grab orgname
        orgname = popup['org']

        # get address is available, otherwise use state, otherwise district
        addr = popup['address'] if popup['address'] is not None else ''
        if not addr and popup['state']:
            addr = popup['state']
        if not addr and popup['district']:
            addr = popup['district']

        # Landlines are for organization, pass mobile for contacts
        phone = None
        if popup['telephone']:
            phone = popup['telephone']

        # if no contacts, get email for organization
        email = list()
        if not popup['contact_name'] and (popup['email1'] or popup['email2']):
            if popup['email1']:
                email.append(popup['email1'][0])
            if popup['email2']:
                email.append(popup['email2'][0])

        # grab url
        url = popup['url']

        # extract contact(s) for organization
        extr_contacts = self._get_org_contacts(popup)

        # build organization item
        organization = ScrapedOrganization(
            name=orgname,
            address=addr,
            types=None,
            phone_numbers=phone,
            emails=email,
            contacts=extr_contacts,
            organization_url=url,
            partners=None)

        return organization
    
    def _get_org_contacts(self, popup):
        # if no contact names, return
        if not popup['contact_name']:
            return None

        # combine mobile numbers
        mobile1 = popup['mobile1'] if popup['mobile1'] is not None else []
        mobile2 = popup['mobile2'] if popup['mobile2'] is not None else []
        numbers = mobile1 + mobile2

        # combine emails
        email1 = popup['email1'] if popup['email1'] is not None else []
        email2 = popup['email2'] if popup['email2'] is not None else []
        emails = email1 + email2

        # for each contact, create contact and add
        i = 0
        contacts = []
        for contact in popup['contact_name']:
            names = self._parse_contact_name([contact])
            first = names[0]
            last = names[1]

            primary = None
            if len(numbers) > i+1:
                primary = numbers[i]

            email = None
            if len(emails) > i+1:
                email = emails[i]

            contact = ScrapedContact(
                first_name = first, 
                last_name = last, 
                primary_phone = primary,
                secondary_phone = None, 
                email = email,
                organization = None, # this will be done automatically
                publications = None,
                position = '') 

            contacts.append(contact)

            i += 1

        return contacts

    def _edit_org(self, org, data = None):
        if org is None:
            return None

        # Edit org name for generic names like "Board"
        if org == "Board" or org == "Committee":
            state = data['state'] if data['state'] is not None else 'Unknown'
            district = data['district'] if data['district'] is not None else 'Unknown'
            org = data['category'] + " (" + state + ', ' + district + ')'
        return org

    def _edit_category(self, category, data = None):
        return category

    def _edit_contact_name(self, contact_name, data = None):
        if contact_name is None:
            return None

        contacts = []
        # if organization is Individual or NPO, split after comma for title
        if data['category'] == "Individual" or data['category'] == "Nodal Police Office":
            name_role_split = contact_name.split(',', 1)
            contacts.append(name_role_split[0])
            if len(name_role_split) > 1:
                data['role'] = name_role_split[1]
        else: # else, each comma delimits another person
            contacts = contact_name.split(',')

        return contacts

    def _edit_serv_area(self, serv_area, data = None):
        return serv_area

    def _edit_interests(self, interests, data = None):
        return interests

    def _edit_address(self, address, data = None):
        return address

    def _edit_state(self, state, data = None):
        return state

    def _edit_district(self, district, data = None):
        return district

    def _edit_url(self, url, data = None):
        new_url = None
        if url:
            parse = urlparse(url)
            new_url = '%s/' % parse.netloc
        return new_url

    def _edit_phone(self, phone, data = None):
        if phone is None:
            return None

        # split phones by comma and /
        phone_wo_slashes = phone.replace('/', ',')
        phones = phone_wo_slashes.split(',')
        parsed_phones = []

        # create our translate helper to get digits
        all = string.maketrans('','')
        nodigs = all.translate(all, string.digits)

        for num in phones:
            # convert to ascii
            ascii = num.encode("ascii", 'ignore')
            if len(ascii) > 4:
                #extract digits
                digit_only = ascii.translate(all, nodigs)
                if len(digit_only) > 0:
                    parsed_phones.append(digit_only)
            elif len(ascii) > 0:
                parsed_phones[len(parsed_phones) - 1] += ('/' + ascii)


        return parsed_phones

    def _edit_email(self, email, data = None):
        if email is None:
            return None
        # split emails on commas or semicolons
        if "," in email:
            return email.split(',')
        return email.split(';')

    def _parse_contact_name(self, contact_name):
        name = contact_name
        if not name:
            first = ''
            last = ''
        else:
            # Split on rightmost space
            # e.g. "first first first first" "last"
            # or "first"
            names = name[0].rsplit(' ', 1)
            first = names[0]
            if len(names) > 1:
                last = names[1]
            else:
                last = ''

        return [first, last]

    def _create_items(self, states, districts, orgnames, categories, contacts, contact_numbers, cids):
        # grab count from states, but should be same for all
        count = len(states)
        urls = [self._map_cid_to_url(cid) for cid in cids]
        
        items = []
        # iterate over states, but we could use anything
        for i in xrange(0, count):
            item = self._TableData(states[i], districts[i],
                                   orgnames[i], urls[i],
                                   categories[i], contacts[i],
                                   contact_numbers[i])
            items.append(item)

        return items

    def _map_cid_to_url(self, cid):
        return "http://www.stoptrafficking.in/ServicesPopup.aspx?cid=" + cid

    # an inner class for storing _TableData
    class _TableData:
        """An intermediate class to hold table data"""

        def __init__(self, state = None, district = None,
                     org_name = None, popup_url = None, categories = None,
                     contacts = None, contact_numbers = None):
            self.state = state
            self.district = district
            self.org_name = org_name
            self.popup_url = popup_url
            self.categories = categories
            self.contacts = contacts
            self.contact_numbers = contact_numbers

        def __str__(self):
            ret = "<" + self.state + ", "
            ret += self.district + ", "
            ret += self.org_name + ", "
            ret += self.popup_url + ", "
            ret += self.categories + ", "
            ret += self.contacts + ", "
            ret += self.contact_numbers + ">"
            return ret