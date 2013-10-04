import re
import string
from scrapy import log
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, TextResponse, HtmlResponse
from WebCrawler.items import ScrapedOrganization, ScrapedContact

class StopTraffickingDotInScraper:
    """An ad hoc scraper for the page: http://www.stoptrafficking.in/Directory.aspx"""

    # parses the onclick attribute for the cid we will use to find the popup windows
    # use first .group(1) to get the cid out
    onclick_re = re.compile(r'^javascript:window\.open\(\'ServicesPopup\.aspx\?cid=(\d+)\',.*$')

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

    def __init__(self):
        pass

    def parse_directory(self, response):
        """Scrape the HttpRequest.Response for Organizations"""

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

            items = self._create_items(states, districts, orgnames, categories, contacts, contact_numbers, cids)

        return items 

    def parse_popup(self, response, table_entry):
        """Parse a Popup from StopTrafficking.in (and integrate with table data)"""

        hxs = HtmlXPathSelector(response)

        # get our data from the cells
        cells = hxs.select('//table/tr/td')

        popup = {}
        popup['org'] = cells.select('span[@id ="lblOrgName"]/text()').extract()
        popup['category'] = cells.select('span[@id ="lblCategory"]/text()').extract()
        popup['contact_name'] = cells.select('span[@id ="lblContactName"]/text()').extract()
        popup['serv_area'] = cells.select('span[@id ="lblServiceArea"]/text()').extract()
        popup['interests'] = cells.select('span[@id ="lblInvolve"]/text()').extract()
        popup['address'] = cells.select('span[@id ="lblAddress"]/text()').extract()
        popup['state'] = cells.select('span[@id ="lblState"]/text()').extract()
        popup['district'] = cells.select('span[@id ="lblDistrict"]/text()').extract()
        popup['url'] = cells.select('span[@id ="lblUrl"]/text()').extract()
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

        names = self._parse_contact_name(popup['contact_name'])
        first = names[0]
        last = names[1]

        telephone = popup['telephone'] if popup['telephone'] != None else []
        mobile1 = popup['mobile1'] if popup['mobile1'] != None else []
        mobile2 = popup['mobile2'] if popup['mobile2'] != None else []
        numbers = telephone + mobile1 + mobile2
        primary_no = None
        sec_no = None
        if len(numbers) > 0:
            primary_no = numbers[0]
        if len(numbers) > 1:
            sec_no = numbers[1]

        email = None
        if popup['email1']:
            email = popup['email1'][0]

        position = None
        if 'role' in popup.keys():
            position = popup['role']

        contact = ScrapedContact(
            first_name = first, 
            last_name = last, 
            primary_phone_number = primary_no,
            secondary_phone_number = sec_no, 
            email_address = email,
            organizations = None,
            publications = None,
            position = '') 
        return contact

    def _create_org(self, popup):
        orgname = popup['org']
        addr = popup['address'] if popup['address'] != None else ''
        if not addr and popup['state']:
            addr = popup['state']
        if not addr and popup['district']:
            addr = popup['district']

        phone = None
        if popup['telephone']:
            phone = popup['telephone'][0]

        email = None
        if not popup['contact_name'] and (popup['email1'] or popup['email2']):
            if popup['email1']:
                email = popup['email1'][0]
            else:
                email = popup['email2'][0]

        url = popup['url']

        extr_contacts = self._get_org_contacts(popup)

        organization = ScrapedOrganization(
            name = orgname,
            address = addr,
            types = None,
            phone_number = phone,
            email_address = email,
            contacts = extr_contacts,
            organization_url = url,
            partners = None)

        return organization
    
    def _get_org_contacts(self, popup):
        if not popup['contact_name']:
            return None


        mobile1 = popup['mobile1'] if popup['mobile1'] != None else []
        mobile2 = popup['mobile2'] if popup['mobile2'] != None else []
        numbers = mobile1 + mobile2

        email1 = popup['email1'] if popup['email1'] != None else []
        email2 = popup['email2'] if popup['email2'] != None else []
        emails = email1 + email2

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
                primary_phone_number = primary,
                secondary_phone_number = None, 
                email_address = email,
                organizations = None, # this will be done automatically
                publications = None,
                position = '') 

            contacts.append(contact)

            i += 1

        return contacts

    def _edit_org(self, org, data = None):
        if org == None:
            return None

        if org == "Board" or org == "Committee":
            state = data['state'] if data['state'] != None else 'Unknown'
            district = data['district'] if data['district'] != None else 'Unknown'
            org = data['category'] + " (" + state + ', ' + district + ')'
        return org

    def _edit_category(self, category, data = None):
        return category

    def _edit_contact_name(self, contact_name, data = None):
        if contact_name == None:
            return None

        contacts = []
        if data['category'] == "Individual" or data['category'] == "Nodal Police Office":
            name_role_split = contact_name.split(',', 1)
            contacts.append(name_role_split[0])
            if len(name_role_split) > 1:
                data['role'] = name_role_split[1]
        else:
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
        return url

    def _edit_phone(self, phone, data = None):
        if phone == None:
            return None

        phones = phone.split(',') 
        parsed_phones = []

        # create our translate helper to get digits
        all = string.maketrans('','')
        nodigs = all.translate(all, string.digits)

        for num in phones:
            ascii = num.encode("ascii", 'ignore')
            if len(ascii) > 0:
                digit_only = ascii.translate(all, nodigs)
                parsed_phones.append(int(float(digit_only)))

        return parsed_phones

    def _edit_email(self, email, data = None):
        if email == None:
            return None
        return email.split(',')

    def _parse_contact_name(self, contact_name):
        name = contact_name
        if not name:
            first = ''
            last = ''
        else:

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