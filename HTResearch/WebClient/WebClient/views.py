from django.http import HttpResponseNotFound
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from springpython.context import ApplicationContext
from mongoengine.fields import StringField, URLField
import string

from HTResearch.DataAccess.dao import OrganizationDAO
from HTResearch.DataAccess.dto import OrganizationDTO
from HTResearch.Utilities.encoder import MongoJSONEncoder
from HTResearch.Utilities.context import DAOContext
from HTResearch.Utilities.logutil import LoggingSection, LoggingUtility
from HTResearch.WebClient.WebClient.settings import GOOGLE_MAPS_API_KEY


logger = LoggingUtility().get_logger(LoggingSection.CLIENT, __name__)


def index(request):
    logger.info('Request made for index')
    args = {}
    args.update(csrf(request))

    args["api_key"] = GOOGLE_MAPS_API_KEY

    return render_to_response('index_template.html', args)


def search(request):

    if request.method == 'POST':
        logger.info('Search request made on index')
        search_text = request.POST['search_text']
    else:
        search_text = ''

    organizations = []

    if search_text:
        ctx = ApplicationContext(DAOContext())
        org_dao = ctx.get_object('OrganizationDAO')

        organizations = org_dao.text_search(search_text, 10, 'name')

        for org in organizations:
            encode_org(org)

    params = {'organizations': organizations}
    return render_to_response('search_results.html', params)


def organization_profile(request):
    uri = request.build_absolute_uri()
    org_dao = OrganizationDAO()

    try:
        org_lookup_key = string.split(uri, '/')[4]
        org = org_dao.find(id=org_lookup_key)
    except Exception as e:
        logger.exception('Exception encountered on organization lookup', e)
        print e.message
        return get_http_404_page(request)

    params = {"organization": org}
    return render_to_response('organization_profile_template.html', params)


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