from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from HTResearch.WebClient.webclient.settings import GOOGLE_MAPS_API_KEY

def index(request):
    t = get_template('index_template.html')
    html = t.render(Context({"api_key": GOOGLE_MAPS_API_KEY}))
    return HttpResponse(html)

def organization_profile(request):
    return HttpResponse("test")