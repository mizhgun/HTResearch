from django.http import HttpResponse, HttpResponseNotFound
from django.template.loader import get_template
from django.template import Context
from HTResearch.Utilities.context import DAOContext
from springpython.context import ApplicationContext
from HTResearch.WebClient.WebClient.settings import GOOGLE_MAPS_API_KEY
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from mongoengine.fields import StringField, URLField
from HTResearch.Utilities.encoder import MongoJSONEncoder


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


def organization_profile(request, org_id):
    ctx = ApplicationContext(DAOContext())
    org_dao = ctx.get_object('OrganizationDAO')

    try:
        org = org_dao.find(id=org_id)
    except Exception as e:
        #If we ever hook up logging, this is where we would log the message
        print e.message
        return get_http_404_page(request)

    t = get_template('organization_profile_template.html')
    html = t.render(Context({"organization": org}))
    return HttpResponse(html)


def contact_profile(request, contact_id):
    ctx = ApplicationContext(DAOContext())
    contact_dao = ctx.get_object('ContactDAO')

    try:
        contact = contact_dao.find(id=contact_id)
    except Exception as e:
        #If we ever hook up logging, this is where we would log the message
        print e.message
        return get_http_404_page(request)

    org_urls = []
    for org in contact.organizations:
        org_urls.append("/organization/"+org.id)

    #Generates a 2d list
    contact.organizations = zip(contact.organizations, org_urls)

    t = get_template('contact_profile_template.html')
    html = t.render(Context({"contact": contact}))
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