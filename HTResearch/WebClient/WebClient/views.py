from datetime import datetime, timedelta
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from springpython.context import ApplicationContext
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from springpython.context import ApplicationContext
from mongoengine.fields import StringField, URLField

from HTResearch.DataAccess.dto import OrganizationDTO
from HTResearch.Utilities.encoder import MongoJSONEncoder
from HTResearch.Utilities.context import DAOContext
from HTResearch.Utilities.logutil import LoggingSection, LoggingUtility
from HTResearch.WebClient.WebClient.settings import GOOGLE_MAPS_API_KEY


logger = LoggingUtility().get_logger(LoggingSection.CLIENT, __name__)
ctx = ApplicationContext(DAOContext())

REFRESH_ADDRESS_LIST = timedelta(minutes=5)

def index(request):
    logger.info('Request made for index')
    args = {}
    args.update(csrf(request))

    args["api_key"] = GOOGLE_MAPS_API_KEY

    return render_to_response('index_template.html', args)


def heatmap_coordinates(request):
    if request.method != 'GET':
        return HttpResponseBadRequest

    addresses = cache.get('organization_address_list')
    last_update = cache.get('organization_address_list_last_update')
    if not addresses or not last_update or (datetime.now() - last_update > REFRESH_ADDRESS_LIST):
        str_addresses = []
        cache.set('organization_address_list_last_update', datetime.now())
        ctx = ApplicationContext(DAOContext())
        org_dao = ctx.get_object('OrganizationDAO')
        organizations = org_dao.findmany(0, address__exists=True, address__ne='')
        for org in organizations:
            str_addresses.append(org.address)

        addresses = MongoJSONEncoder().encode(str_addresses)

        if len(addresses) > 0:
            cache.set('organization_address_list', addresses)

    return HttpResponse(addresses, content_type="application/json")


def search(request):
    if request.method == 'POST':
        search_text = request.POST['search_text']
        logger.info('Search request made with search_text=%s' % search_text)
    else:
        search_text = ''

    organizations = []

    if search_text:
        org_dao = ctx.get_object('OrganizationDAO')

        organizations = org_dao.text_search(search_text, 10, 'name')

        for org in organizations:
            encode_org(org)

    params = {'organizations': organizations}
    return render_to_response('search_results.html', params)


def organization_profile(request, org_id):
    logger.info('Request made for profile of org_id=%s' % org_id)
    org_dao = ctx.get_object('OrganizationDAO')

    try:
        org = org_dao.find(id=org_id)
    except Exception as e:
        logger.exception('Exception encountered on organization lookup for org_id=%s' % org_id, e)
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
        logger.exception('Exception encountered on contact lookup for contact_id=%s' % contact_id, e)
        print e.message
        return get_http_404_page(request)

    org_urls = []
    for org in contact.organizations:
        org_urls.append("/organization/"+org.id)

    #Generates a 2d list
    contact.organizations = zip(contact.organizations, org_urls)

    params = {"contact": contact}
    return render_to_response('contact_profile_template.html', params)


def get_http_404_page(request):
    return HttpResponseNotFound('http_404.html')


def unimplemented(request):
    return render_to_response('unimplemented.html')


# Encodes the fields to JSON
def encode_org(org):
    # Make each organization non-string attribute into valid JSON
    fields_dict = OrganizationDTO._fields
    string_types = (StringField, URLField)
    json_fields = [key for key in fields_dict.iterkeys() if type(fields_dict[key]) not in string_types]
    # Find all non-string fields
    for field in json_fields:
        org[field] = MongoJSONEncoder().encode(org[field])