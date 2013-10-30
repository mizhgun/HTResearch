from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from HTResearch.WebClient.webclient.settings import GOOGLE_MAPS_API_KEY
from HTResearch.DataModel.model import Organization

def index(request):
    t = get_template('index_template.html')
    html = t.render(Context({"api_key": GOOGLE_MAPS_API_KEY}))
    return HttpResponse(html)

def organization_profile(request):
    t = get_template('organization_profile_template.html')
    org = Organization(name="Bee Yee Foundation",
                             address="1313 Yee Drive",
                             phone_numbers=4029813230,
                             email_key="beeyee@yeemail.com",
                             organization_url="http://beeyee.com",
                             facebook="facebook.com/yeeeeeee",
                             twitter="BYeeeeeee")
    html = t.render(Context({"organization": org}))
    return HttpResponse(html)