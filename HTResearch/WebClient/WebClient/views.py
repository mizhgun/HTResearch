from django.http import HttpResponse, HttpResponseNotFound
from django.template.loader import get_template
from django.template import Context
from HTResearch.WebClient.WebClient.settings import GOOGLE_MAPS_API_KEY
from HTResearch.DataAccess.dao import OrganizationDAO
import string


def index(request):
    t = get_template('index_template.html')
    html = t.render(Context({"api_key": GOOGLE_MAPS_API_KEY}))
    return HttpResponse(html)

def organization_profile(request):
    uri = request.build_absolute_uri()
    org_dao = OrganizationDAO()

    try:
        org_lookup_key = int(string.split(uri,'/')[4])
        org = org_dao.find(id=org_lookup_key)
    except Exception as e:
        #If we ever hook up logging, this is where we would log the message
        print e.message
        return get_http_404_page()

    t = get_template('organization_profile_template.html')
    html = t.render(Context({"organization": org}))
    return HttpResponse(html)

def get_http_404_page():
    template = get_template('http_404.html')
    html = template.render(Context({}))
    return HttpResponseNotFound(html)