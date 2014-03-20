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
#endregion

@decorators.safe_apicall
def get_org_keywords(request):
    if request.method == 'GET':
        org_id = request.GET['org_id']
    else:
        org_id = ''

    org_dao = ctx.get_object('OrganizationDAO')
    org = org_dao.find(id=org_id)
    keywords = org.keywords.split(' ')
    return HttpResponse(json.dumps(keywords), mimetype='application/json')


def get_org_rank_rows(request):
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
def org_partner_map(request):
    """
    Generates the data needed to display the organization partner map and then stores it in the
    cache. Data returned as a JSON string.

    request: HttpRequest from Django (GET)
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
                org = org_dao.find(id=u['organization'].id)
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
    return HttpResponse(MongoJSONEncoder().encode(data), content_type="application/json")