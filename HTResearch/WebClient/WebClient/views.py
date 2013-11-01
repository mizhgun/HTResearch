from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from HTResearch.WebClient.WebClient.settings import GOOGLE_MAPS_API_KEY
from HTResearch.DataAccess.dao import OrganizationDAO
from HTResearch.DataAccess.factory import DAOFactory
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
import json
import pdb

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

    org_dao = DAOFactory.get_instance(OrganizationDAO)
    organizations = [org_dao.find(name=search_text)]

    params = {'organizations': organizations}
    return render_to_response('search_results.html', params)