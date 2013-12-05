from urlparse import urlparse
from datetime import datetime, timedelta
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.template.loader import get_template
from django.template import Context
from springpython.context import ApplicationContext
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from mongoengine.fields import StringField, URLField, EmailField
from springpython.context import ApplicationContext
from HTResearch.Utilities.encoder import MongoJSONEncoder
from HTResearch.Utilities.context import DAOContext
from HTResearch.Utilities.logutil import LoggingSection, LoggingUtility
from HTResearch.WebClient.WebClient.settings import GOOGLE_MAPS_API_KEY
import json


logger = LoggingUtility().get_logger(LoggingSection.CLIENT, __name__)
ctx = ApplicationContext(DAOContext())
REFRESH_COORDS_LIST = timedelta(minutes=5)


def index(request):
    logger.info('Request made for index')
    args = {}
    args.update(csrf(request))

    args["api_key"] = GOOGLE_MAPS_API_KEY

    return render_to_response('index_template.html', args)


def heatmap_coordinates(request):
    if request.method != 'GET':
        return HttpResponseBadRequest

    coords = cache.get('organization_coords_list')
    last_update = cache.get('organization_coords_list_last_update')
    if not coords or not last_update or (datetime.now() - last_update > REFRESH_COORDS_LIST):
        new_coords = []
        cache.set('organization_address_list_last_update', datetime.now())
        ctx = ApplicationContext(DAOContext())
        org_dao = ctx.get_object('OrganizationDAO')
        organizations = org_dao.findmany(latlng__exists=True, latlng__ne=[])
        for org in organizations:
            new_coords.append(org.latlng)

        coords = MongoJSONEncoder().encode(new_coords)

        if len(coords) > 0:
            cache.set('organization_coords_list', coords)

    return HttpResponse(coords, content_type="application/json")


def search_organizations(request):

    if request.method == 'GET':
        search_text = request.GET['search_text']
        logger.info('Search request made with search_text=%s' % search_text)
    else:
        search_text = ''

    organizations = []

    if search_text:
        org_dao = ctx.get_object('OrganizationDAO')

        organizations = org_dao.text_search(search_text, 10, 'name')

        for dto in organizations:
            encode_dto(dto)

    params = {'organizations': organizations}
    return render_to_response('org_search_results.html', params)


def search_contacts(request):

    if request.method == 'GET':
        search_text = request.GET['search_text']
    else:
        search_text = ''

    contacts = []

    if search_text:
        ctx = ApplicationContext(DAOContext())
        contact_dao = ctx.get_object('ContactDAO')

        contacts = contact_dao.text_search(search_text, 10, 'last_name')

        for dto in contacts:
            encode_dto(dto)

    params = {'contacts': contacts}
    return render_to_response('contact_search_results.html', params)


def organization_profile(request, org_id):
    logger.info('Request made for profile of org_id=%s' % org_id)
    org_dao = ctx.get_object('OrganizationDAO')

    try:
        org = org_dao.find(id=org_id)
    except Exception as e:
        logger.error('Exception encountered on organization lookup for org_id=%s' % org_id)
        print e.message
        return get_http_404_page(request)

    params = {"organization": org}
    return render_to_response('organization_profile_template.html', params)


def contact_profile(request, contact_id):
    logger.info('Request made for profile of contact_id=%s' % contact_id)
    contact_dao = ctx.get_object('ContactDAO')

    try:
        contact = contact_dao.find(id=contact_id)
    except Exception as e:
        logger.error('Exception encountered on contact lookup for contact_id=%s' % contact_id)
        print e.message
        return get_http_404_page(request)

    org_url = '/organization/'+contact.organization.id if contact.organization else ''

    params = {"contact": contact,
              "org_url": org_url}

    return render_to_response('contact_profile_template.html', params)


def org_rank(request, sort_method=''):
    return render_to_response('org_rank.html')


def get_org_rank_rows(request):
    start = int(request.GET['start'])
    end = int(request.GET['end'])
    sort = request.GET['sort']

    org_dao = ctx.get_object('OrganizationDAO')
    organizations = list(org_dao.findmany(start=start, end=end, sort_fields=sort))

    # add netloc to urls if needed
    for org in organizations:
        if org.organization_url is not None:
            netloc = urlparse(org.organization_url).netloc
            if netloc == "":
                org.organization_url = "//" + org.organization_url


    params = {'organizations': organizations}
    return render_to_response('org_rank_row.html', params)


def login(request):
    return render_to_response('login.html')


def signup(request):
    return render_to_response('signup.html')


def get_http_404_page(request):
    template = get_template('404.html')
    html = template.render(Context({}))
    return HttpResponseNotFound(html, status=404)


def unimplemented(request):
    return render_to_response('unimplemented.html')


# Encodes a DTO's non-string fields to JSON
def encode_dto(dto):
    dto_type = type(dto)
    fields_dict = dto_type._fields
    string_types = (StringField, URLField, EmailField)
    json_fields = [key for key in fields_dict.iterkeys() if type(fields_dict[key]) not in string_types]
    for field in json_fields:
        dto[field] = MongoJSONEncoder().encode(dto[field])

def get_org_keywords(request):
    if request.method == 'GET':
        org_id = request.GET['org_id']
    else:
        org_id = ''

    org_dao = ctx.get_object('OrganizationDAO')
    org = org_dao.find(id=org_id)
    #Commenting out instead of deleting for demo purposes
    #If keywords aren't in the database, you should uncomment this and use Bombay Teen Challenge
    #org.keywords = {'access': 32, 'addicts': 51, 'afraid': 32, 'allows': 32, 'ambedkar': 32,
    #                'announced': 32, 'ashes': 32, 'bandra': 32, 'beauty': 32, 'began': 32,
    #                'betrayed': 32, 'blog': 32, 'blogs': 32, 'bombay': 384, 'bound': 32,
    #                'btc': 64, 'care': 51, 'challenge': 358, 'children': 64, 'contact': 64,
    #                'donate': 64, 'drug': 64, 'education': 89, 'education.': 39, 'gift': 64,
    #                'health': 96, 'homes': 83, 'india': 64, 'light': 64, 'live': 64, 'lives': 96,
    #                'men': 53, 'mumbai': 102, 'music': 83, 'office': 38, 'out.': 39, 'programs': 53,
    #                'read': 96, 'red': 64, 'rescued': 83, 'safe': 53, 'seek': 160, 'streets': 64,
    #                'teen': 384, 'tel': 34, 'training': 51, 'trust': 64, 'vocational': 96, 'women': 112}
    return HttpResponse(json.dumps(org.keywords), mimetype='application/json')
