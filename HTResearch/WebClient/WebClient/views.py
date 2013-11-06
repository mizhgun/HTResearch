from django.http import HttpResponse, HttpResponseNotFound
from django.template.loader import get_template
from django.template import Context
from HTResearch.WebClient.WebClient.settings import GOOGLE_MAPS_API_KEY
from HTResearch.DataModel.model import *
import string


def index(request):
    t = get_template('index_template.html')
    html = t.render(Context({"api_key": GOOGLE_MAPS_API_KEY}))
    return HttpResponse(html)


def organization_profile(request):
    uri = request.build_absolute_uri()
    org_lookup_key = 0
    org = None
    try:
        org_lookup_key = int(string.split(uri,'/')[4])
    except ValueError:
        return get_http_404_page()

    #DUMMY DATA BEGINS
    my_contact = Contact(first_name="Jordan",
                             last_name="Degner",
                             primary_phone=4029813230,
                             email="jdegner0129@gmail.com",
                             position="Software Engineer")
    my_contact2 = Contact(first_name="John",
                             last_name="Marth",
                             primary_phone=5555555555,
                             email="marth@yeemail.com",
                             position="Tipper")

    people = [my_contact, my_contact2, my_contact2, my_contact2, my_contact]
    partner = Organization(name="Melee it on Me",
                             address="Turtle Drive",
                             contacts= people,
                             phone_numbers=5551234597,
                             email_key="marth@marthmail.com",
                             organization_url="http://www.smashboards.com",
                             facebook="facebook.com/smashboards",
                             twitter="smashboards")
    partners = [partner]
    org = Organization(name="Bee Yee Foundation",
                             address="1313 Yee Drive",
                             contacts= people,
                             partners=partners,
                             phone_numbers=4029813230,
                             email_key="beeyee@yeemail.com",
                             organization_url="http://beeyee.com",
                             facebook="facebook.com/yeeeeeee",
                             twitter="BYeeeeeee")
    #END DUMMY DATA

    if org_lookup_key == 0 or org is None:
        return get_http_404_page()

    t = get_template('organization_profile_template.html')
    html = t.render(Context({"organization": org}))
    return HttpResponse(html)

def get_http_404_page():
    template = get_template('http_404.html')
    html = template.render(Context({}))
    return HttpResponseNotFound(html)