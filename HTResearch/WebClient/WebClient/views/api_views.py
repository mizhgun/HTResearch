# stdlib imports
import json
from urlparse import urlparse
from datetime import datetime, timedelta
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseBadRequest
from springpython.context import ApplicationContext

# project imports
from HTResearch.DataModel.enums import OrgTypesEnum
from HTResearch.Utilities.context import DAOContext
from HTResearch.Utilities.logutil import LoggingSection, get_logger
from HTResearch.WebClient.WebClient.views.shared_views import get_http_404_page
from HTResearch.Utilities.encoder import MongoJSONEncoder
from HTResearch.Utilities import decorators

#region Globals
logger = get_logger(LoggingSection.CLIENT, __name__)
ctx = ApplicationContext(DAOContext())
REFRESH_COORDS_LIST = timedelta(minutes=5)
REFRESH_PARTNER_MAP = timedelta(minutes=5)
REFRESH_ORG_BREAKDOWN = timedelta(minutes=5)
REFRESH_COUNT = timedelta(minutes=5)
#endregion

@decorators.safe_apicall
def get_org_keywords(request):
    """
    Retrieves the organization's keywords to create the word cloud on the profile page.

    Returns:
        List of keywords encoded in JSON.
    """
    if request.method == 'GET':
        org_id = request.GET['org_id']
    else:
        org_id = ''

    org_dao = ctx.get_object('OrganizationDAO')
    org = org_dao.find(id=org_id)
    keywords = org.keywords.split(' ')
    return HttpResponse(json.dumps(keywords), mimetype='application/json')


def get_org_rank_rows(request):
    """
    Retrieves the organization information to populate the org-rank page.

    Returns:
        Dictionary of the organization info and the count.
    """
    start = int(request.GET['start'])
    end = int(request.GET['end'])
    if 'search' in request.GET:
        search = request.GET['search']
    else:
        search = None
    if 'sort' in request.GET:
        sort = request.GET['sort']
    else:
        sort = ()

    org_dao = ctx.get_object('OrganizationDAO')
    organizations = list(org_dao.findmany(start=start, end=end, sort_fields=[sort], search=search))
    records = org_dao.count(search)

    # add netloc to urls if needed
    for org in organizations:
        if org.organization_url is not None:
            netloc = urlparse(org.organization_url).netloc
            if netloc == "":
                org.organization_url = "//" + org.organization_url

    obj = {
        'data': organizations,
        'records': records
    }

    return HttpResponse(MongoJSONEncoder().encode(obj), content_type="application/text")


@decorators.safe_apicall
def heatmap_coordinates(request):
    """
    Gets all the lat/long values for all organizations.

    Returns:
        List of lat/long coordinates encoded in JSON.
    """
    if request.method != 'GET':
        return HttpResponseBadRequest

    coords = cache.get('organization_coords_list')
    last_update = cache.get('organization_coords_list_last_update')
    if not coords or not last_update or (datetime.utcnow() - last_update > REFRESH_COORDS_LIST):
        new_coords = []
        cache.set('organization_address_list_last_update', datetime.utcnow())
        ctx = ApplicationContext(DAOContext())
        org_dao = ctx.get_object('OrganizationDAO')
        organizations = org_dao.findmany(latlng__exists=True, latlng__ne=[])
        for org in organizations:
            new_coords.append(org.latlng)

        coords = MongoJSONEncoder().encode(new_coords)

        if len(coords) > 0:
            cache.set('organization_coords_list', coords)

    return HttpResponse(coords, content_type="application/json")


@decorators.safe_apicall
def org_count(request):
    """
    Gets the total organization count.

    Returns:
        Total number of organizations.
    """
    user_id = request.session['user_id'] if 'user_id' in request.session else None

    logger.info('Publication count request made by user {0}'.format(user_id))

    # Cache organization count
    count = cache.get('organization_count')
    last_update = cache.get('organization_count_last_update')
    if not count or not last_update or (datetime.utcnow() - last_update > REFRESH_COUNT):

        cache.set('organization_count_last_update', datetime.utcnow())

        org_dao = ctx.get_object('OrganizationDAO')
        count = ''
        try:
            count = org_dao.count()
        except:
            logger.error('Exception encountered on organziation count by user={0}'.format(user_id))

        cache.set('organization_count', count)

    data = {
        'count': count
    }

    return HttpResponse(json.dumps(data), content_type='application/json')


@decorators.safe_apicall
def contact_count(request):
    """
    Gets the total contact count.

    Returns:
        Total number of contacts.
    """
    user_id = request.session['user_id'] if 'user_id' in request.session else None

    logger.info('Contact count request made by user {0}'.format(user_id))

    # Cache contact count
    count = cache.get('contact_count')
    last_update = cache.get('contact_count_last_update')
    if not count or not last_update or (datetime.utcnow() - last_update > REFRESH_COUNT):

        cache.set('contact_count_last_update', datetime.utcnow())

        contact_dao = ctx.get_object('ContactDAO')
        user_dao = ctx.get_object('UserDAO')

        contacts_count = 0
        user_count = 0
        try:
            contacts_count = contact_dao.count()
        except:
            logger.error('Exception encountered on contact count by user={0}'.format(user_id))

        try:
            user_count = user_dao.count()
        except:
            logger.error('Exception encountered on user count by user={0}'.format(user_id))

        count = contacts_count + user_count

        cache.set('contact_count', count)

    data = {
        'count': count
    }

    return HttpResponse(json.dumps(data), content_type='application/json')


@decorators.safe_apicall
def pub_count(request):
    """
    Gets the total publication count.

    Returns:
        Total number of publications.
    """
    user_id = request.session['user_id'] if 'user_id' in request.session else None

    logger.info('Publication count request made by user {0}'.format(user_id))

    # Cache publication count
    count = cache.get('publication_count')
    last_update = cache.get('publication_count_last_update')
    if not count or not last_update or (datetime.utcnow() - last_update > REFRESH_COUNT):

        cache.set('publication_count_last_update', datetime.utcnow())

        pub_dao = ctx.get_object('PublicationDAO')

        try:
            count = pub_dao.count()
        except:
            logger.error('Exception encountered on publication count by user={0}'.format(user_id))

        cache.set('publication_count', count)

    data = {
        'count': count
    }

    return HttpResponse(json.dumps(data), content_type='application/json')


@decorators.safe_apicall
def org_partner_map(request):
    """
    Generates the data needed to display the organization partner map and then stores it in the
    cache. Data returned as a JSON string.

    Returns:
        Partner map configurations encoded in JSON.
    """
    if request.method != 'GET':
        return HttpResponseBadRequest

    pmap = cache.get('partner_map')
    last_update = cache.get('partner_map_last_update')
    if not pmap or not last_update or (datetime.utcnow() - last_update > REFRESH_PARTNER_MAP):
        new_pmap = {
            "nodes": [],
            "links": [],
            "threeps": {
                "PREVENTION": OrgTypesEnum.PREVENTION,
                "PROTECTION": OrgTypesEnum.PROTECTION,
                "PROSECUTION": OrgTypesEnum.PROSECUTION
            }
        }
        cache.set('partner_map_last_update', datetime.utcnow())
        ctx = ApplicationContext(DAOContext())
        org_dao = ctx.get_object('OrganizationDAO')
        organizations = org_dao.all('name', 'id', 'partners', 'types', 'address')
        i = 0
        for org in organizations:
            new_pmap["nodes"].append({
                "name": org.name,
                "id": str(org.id),
                "types": org.types,
                "addr": org.address
            })
            for part in org.partners:
                partner_id = str(part.id)
                for j in xrange(0, i):
                    if new_pmap["nodes"][j]["id"] == partner_id:
                        new_pmap["links"].append({
                           "source": i,
                           "target": j
                        })

            i += 1

        pmap = MongoJSONEncoder().encode(new_pmap)

        cache.set('partner_map', pmap)

    return HttpResponse(pmap, content_type="application/json")


def search_publications(request):
    """
    Searches for publications based on the search text.

    Returns:
        A { 'results' : list of JSON-encoded Publications } dictionary for the search results of Publications.
    """
    user_id = request.session['user_id'] if 'user_id' in request.session else None

    if request.method == 'GET':
        search_text = request.GET['search_text']
        logger.info('Search request made for publications with search_text={0} by user {1}'.format(
            search_text, user_id))
    else:
        search_text = ''

    publications = []

    if search_text:
        pub_dao = ctx.get_object('PublicationDAO')
        try:
            publications = pub_dao.findmany(search=search_text,
                                            num_elements=10,
                                            sort_fields=['valid', 'title'],
                                            valid=True)
        except:
            logger.error('Exception encountered on publication search with search_text={0}'.format(search_text))
            return get_http_404_page(request)

    results = []
    for dto in publications:
        pub = dto.__dict__['_data']
        # Change the datetime to make it readable in the modal
        pub['publication_date'] = str(pub['publication_date'].year)
        results.append(pub)

    data = {'results': results}
    return HttpResponse(MongoJSONEncoder().encode(data), content_type='application/json')


def search_contacts(request):
    """
    Searches for contacts based on the search text.

    Returns:
        A { 'results' : list of JSON-encoded Contacts } dictionary for the search results of Contacts.
    """
    user_id = request.session['user_id'] if 'user_id' in request.session else None

    if request.method == 'GET':
        search_text = request.GET['search_text']
        logger.info('Search request made for contacts with search_text={0} by user {1}'.format(search_text, user_id))
    else:
        search_text = ''

    contacts = []
    users = []

    if search_text:
        contact_dao = ctx.get_object('ContactDAO')
        try:
            contacts = contact_dao.findmany(search=search_text,
                                            num_elements=10,
                                            sort_fields=['valid', 'content_weight', 'last_name', 'first_name'],
                                            valid=True)
        except:
            logger.error('Exception encountered on contact search with search_text={0}'.format(search_text))
            return get_http_404_page(request)

        if user_id:
            user_dao = ctx.get_object('UserDAO')
            try:
                users = user_dao.findmany(search=search_text,
                                          num_elements=10,
                                          sort_fields=['valid', 'content_weight', 'last_name', 'first_name'])
            except:
                logger.error('Exception encountered on user search with search_text={0}'.format(search_text))
                return get_http_404_page(request)

    results = []
    for dto in contacts:
        c = dto.__dict__['_data']
        org_dao = ctx.get_object('OrganizationDAO')
        try:
            if c['organization']:
                org = org_dao.find(id=c['organization'].id)
                #Prevent adding this field as it cannot be properly encoded
                org.page_rank_info = None
                c['organization'] = org.__dict__['_data']
        except:
            logger.error('Exception encountered on organization search with search_text={0}'.format(search_text))
            return get_http_404_page(request)
        c['type'] = 'contact'
        results.append(c)

    for dto in users:
        u = dto.__dict__['_data']
        org_dao = ctx.get_object('OrganizationDAO')
        try:
            if u['organization']:
                org = org_dao.find(id=u['organization'].id).exclude('page_rank_info')
                #Prevent adding this field as it cannot be properly encoded
                org.page_rank_info = None
                u['organization'] = org.__dict__['_data']
        except:
            logger.error('Exception encountered on organization search with search_text={0}'.format(search_text))
            return get_http_404_page(request)
        u['type'] = 'user'
        results.append(u)

    results = sorted(results, key=lambda k: (k['first_name'], k['last_name'], k['content_weight']))[:10]

    # Add the org types to show
    # for index, contact in enumerate(results):
    #     if contact['organization'] and contact['organization']['types']:
    #         type_nums = contact['organization']['types']
    #         org_types = []
    #         for org_type in type_nums:
    #             org_types.append(OrgTypesEnum.reverse_mapping[org_type].title())
    #         results[index]['organization']['types'] = org_types

    data = {'results': results}
    return HttpResponse(MongoJSONEncoder().encode(data), content_type="application/json")


def search_organizations(request):
    """
    Searches for organizations based on the search text.

    Returns:
        A { 'results' : list of JSON-encoded Organizations } dictionary for the search results of Organizations.
    """
    user_id = request.session['user_id'] if 'user_id' in request.session else None

    if request.method == 'GET':
        search_text = request.GET['search_text']
        logger.info(
            'Search request made for organizations with search_text={0} by user={1}'.format(search_text, user_id))
    else:
        search_text = ''

    organizations = []

    if search_text:
        org_dao = ctx.get_object('OrganizationDAO')
        try:
            organizations = org_dao.findmany(search=search_text, num_elements=10,
                                             sort_fields=['valid', 'combined_weight', 'name'],
                                             valid=True)
            for org in organizations:
                org.page_rank_info = None
        except:
            logger.error('Exception encountered on organization search with search_text={0}'.format(search_text))
            return get_http_404_page(request)

    results = []
    for dto in organizations:
        org = dto.__dict__['_data']
        # Split organization keyword string into list of words
        org['keywords'] = (org['keywords'] or '').split()
        results.append(org)
    data = {'results': results}
    json_data = MongoJSONEncoder().encode(data)
    return HttpResponse(json_data, content_type="application/json")


@decorators.safe_apicall
def orgs_by_region(request):
    """
    Gets the organization count by each region in India.

    Returns:
        Organization counts by region, encoded in JSON. Includes the total number of organizations and the total whose
        region is known.
    """

    user_id = request.session['user_id'] if 'user_id' in request.session else None

    logger.info('Org breakdown by region request made by user {0}'.format(user_id))

    orgs_json = cache.get('orgs_by_region')
    last_update = cache.get('orgs_by_region_last_update')
    if not orgs_json or not last_update or (datetime.utcnow() - last_update > REFRESH_ORG_BREAKDOWN):
        cache.set('orgs_by_region_last_update', datetime.utcnow())

        org_dao = ctx.get_object('OrganizationDAO')

        regions = [
            'Uttar Pradesh', 'Maharashtra', 'Bihar', 'West Bengal', 'Andhra Pradesh', 'Madhya Pradesh', 'Tamil Nadu',
            'Rajasthan', 'Karnataka', 'Gujarat', 'Odisha', 'Kerala', 'Jharkhand', 'Assam', 'Punjab', 'Chhattisgarh',
            'Haryana', 'Jammu and Kashmir', 'Uttarakhand', 'Himachal Pradesh', 'Tripura', 'Meghalaya', 'Manipur',
            'Nagaland', 'Goa', 'Arunachal Pradesh', 'Mizoram', 'Sikkim', 'Delhi', 'Puducherry', 'Chandigarh', 'Andaman',
            'Nicobar Islands', 'Dadra', 'Nagar Haveli', 'Daman', 'Diu', 'Lakshadweep',
        ]

        region_count = {}
        results = []
        # Total count in known categories
        total_known = 0

        organizations = list(org_dao.findmany())
        for org in organizations:
            if org['address']:
                for region in regions:
                    if region in org['address']:
                        if region in region_count:
                            region_count[region] += 1
                        else:
                            region_count[region] = 1
                        break

        for key in region_count.iterkeys():
            count = region_count[key]
            total_known += count
            results.append({
                'label': key,
                'value': count,
            })

        total = org_dao.count()

        data = {
            'categories': results,
            'total': total,
            'total_known': total_known,
        }
        orgs_json = json.dumps(data)
        cache.set('orgs_by_region', orgs_json)

    return HttpResponse(orgs_json, content_type='application/json')


@decorators.safe_apicall
def orgs_by_type(request):
    """
    Gets the organization count by each organization type.

    Returns:
        Organization counts by type, encoded in JSON. Includes the total number of organizations and the total whose
        type is known.
    """

    user_id = request.session['user_id'] if 'user_id' in request.session else None

    logger.info('Org breakdown by type request made by user {0}'.format(user_id))

    orgs_json = cache.get('orgs_by_type')
    last_update = cache.get('orgs_by_type_last_update')
    if not orgs_json or not last_update or (datetime.utcnow() - last_update > REFRESH_ORG_BREAKDOWN):
        cache.set('orgs_by_type_last_update', datetime.utcnow())

        org_dao = ctx.get_object('OrganizationDAO')

        results = []
        type_count = {}
        # Total count in known categories
        total_known = 0

        for i in range(len(OrgTypesEnum.mapping)):
            key = OrgTypesEnum.reverse_mapping[i]
            orgs = org_dao.findmany(types=i)
            type_count[key] = len(orgs)
            total_known += len(orgs)

        for key in type_count.iterkeys():
            count = type_count[key]
            total_known += count
            results.append({
                'label': key.lower(),
                'value': count,
            })

        # Sort results by value and put unknown at end
        results = sorted(results, key=lambda x: x['value'], reverse=True)
        results = sorted(results, key=lambda x: 1 if x['label'] == 'unknown'
                                           else 0)

        total = org_dao.count()

        data = {
            'categories': results,
            'total': total,
            'total_known': total_known,
        }
        orgs_json = json.dumps(data)
        cache.set('orgs_by_type', orgs_json)

    return HttpResponse(orgs_json, content_type='application/json')


@decorators.safe_apicall
def orgs_by_members(request):
    """
    Gets the organization count by number of members.

    Returns:
        Organization counts by members, encoded in JSON. Includes the total number of organizations and the total whose
        number of organizations whose member count is shown.
    """

    user_id = request.session['user_id'] if 'user_id' in request.session else None

    logger.info('Org breakdown by members request made by user {0}'.format(user_id))

    orgs_json = cache.get('orgs_by_members')
    last_update = cache.get('orgs_by_members_last_update')
    if not orgs_json or not last_update or (datetime.utcnow() - last_update > REFRESH_ORG_BREAKDOWN):
        cache.set('orgs_by_members_last_update', datetime.utcnow())

        org_dao = ctx.get_object('OrganizationDAO')

        ranges = [
            (1, 3, '1-3'),
            (4, 6, '4-6'),
            (7, 9, '7-9'),
            (10, 12, '10+'),
        ]

        results = []
        # Total count in known categories
        total_known = 0

        for r in ranges:
            count = 0
            for i in range(r[0], r[1] + 1):
                count += org_dao.count(contacts__size=i)

            total_known += count

            results.append({
                'label': r[2],
                'value': count,
            })

        total = org_dao.count()

        data = {
            'categories': results,
            'total': total,
            'total_known': total_known
        }
        orgs_json = json.dumps(data)
        cache.set('orgs_by_members', orgs_json)

    return HttpResponse(orgs_json, content_type='application/json')
