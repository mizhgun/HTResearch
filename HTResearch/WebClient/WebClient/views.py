from django.http import HttpResponse, HttpResponseNotFound
from django.template.loader import get_template
from django.template import Context
from HTResearch.Utilities.context import DAOContext
from springpython.context import ApplicationContext
from HTResearch.WebClient.WebClient.settings import GOOGLE_MAPS_API_KEY
from HTResearch.DataAccess.dao import OrganizationDAO
from HTResearch.DataAccess.dto import OrganizationDTO
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from mongoengine.fields import StringField, URLField
import json
from mongoengine.fields import ObjectId
import string
import pdb


class MongoJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

    def encode(self, o):
        result = super(MongoJSONEncoder, self).encode(o)
        if isinstance(o, ObjectId):
            result = result[1:-1]
        return result


def index(request):
    args = {}
    args.update(csrf(request))

    args["api_key"] = GOOGLE_MAPS_API_KEY

    return render_to_response('index_template.html', args)


def search(request):
    if request.method == 'POST':
        search_text = request.POST['search_text']
    else:
        search_text = ''

    organizations = []

    if search_text:
        ctx = ApplicationContext(DAOContext())
        org_dao = ctx.get_object('OrganizationDAO')

        organizations = org_dao.text_search(search_text, 10, 'name')

        for org in organizations:
            # Find all non-string fields
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
        #If we ever hook up logging, this is where we would log the message
        print e.message
        return get_http_404_page()

    #encode_org(org)

    t = get_template('organization_profile_template.html')
    html = t.render(Context({"organization": org}))
    return HttpResponse(html)


def encode_org(org):
     # Make each organization non-string attribute into valid JSON
    fields_dict = OrganizationDTO._fields
    string_types = (StringField, URLField)
    json_fields = [key for key in fields_dict.iterkeys() if type(fields_dict[key]) not in string_types]
    # Find all non-string fields
    for field in json_fields:
        org[field] = MongoJSONEncoder().encode(org[field])


def get_http_404_page():
    template = get_template('http_404.html')
    html = template.render(Context({}))
    return HttpResponseNotFound(html)
