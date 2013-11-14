from django.http import HttpResponse, HttpResponseNotFound
from django.template.loader import get_template
from django.template import Context
from HTResearch.Utilities.context import DAOContext
from springpython.context import ApplicationContext
from HTResearch.WebClient.WebClient.settings import GOOGLE_MAPS_API_KEY
from HTResearch.DataAccess.dao import *
from HTResearch.DataModel.model import *
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from mongoengine.fields import StringField, URLField
from HTResearch.Utilities.encoder import MongoJSONEncoder
import string


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
        return get_http_404_page(request)

    t = get_template('organization_profile_template.html')
    html = t.render(Context({"organization": org}))
    return HttpResponse(html)


def contact_profile(request):
    uri = request.build_absolute_uri()
    contact_dao = ContactDAO()

    #try:
    #    contact_lookup_key = string.split(uri, '/')[4]
    #    contact = contact_dao.find(id=contact_lookup_key)
    #except Exception as e:
    #    #If we ever hook up logging, this is where we would log the message
    #    print e.message
    #    return get_http_404_page(request)

    contact = Contact(first_name="Djordan",
                               last_name="Djeggnerzor",
                               email="jdegner0129@gmail.com",
                               primary_phone="402-555-5555",
                               secondary_phone="402-333-3333",
                               organizations=[],
                               position="Captain of PewPewPew and Anal Incineration")

    #TODO
    #Iterate over organizations and pass a list of URLs to our site
    org_urls = []
    for org in contact.organizations:
        org_urls.append("/organization/"+org.id)

    t = get_template('contact_profile_template.html')
    html = t.render(Context({"contact": contact, "org_urls": org_urls}))
    return HttpResponse(html)


def get_http_404_page(request):
    template = get_template('http_404.html')
    html = template.render(Context({}))
    return HttpResponseNotFound(html)

def unimplemented(request):
    template = get_template('unimplemented.html')
    html = template.render(Context({}))
    return HttpResponse(html)

# Encodes the fields to JSON
def encode_org(org):
    # Make each organization non-string attribute into valid JSON
    fields_dict = OrganizationDTO._fields
    string_types = (StringField, URLField)
    json_fields = [key for key in fields_dict.iterkeys() if type(fields_dict[key]) not in string_types]
    # Find all non-string fields
    for field in json_fields:
        org[field] = MongoJSONEncoder().encode(org[field])