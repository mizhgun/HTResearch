from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from HTResearch.WebClient.WebClient.settings import GOOGLE_MAPS_API_KEY
from HTResearch.DataAccess.dao import OrganizationDAO
from HTResearch.DataAccess.dto import OrganizationDTO
from HTResearch.DataAccess.factory import DAOFactory
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from mongoengine.fields import StringField, URLField
from bson.json_util import dumps
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

    organizations = org_dao.text_search(search_text, 10, 'name')

    # Make each organization non-string attribute into valid JSON
    fields_dict = OrganizationDTO._fields
    string_types = (StringField, URLField)
    json_fields = [key for key in fields_dict.iterkeys() if type(fields_dict[key]) not in string_types]
    for org in organizations:
        # Find all non-string fields
        for field in json_fields:
            org[field] = dumps(org[field])

    params = {'organizations': organizations}
    return render_to_response('search_results.html', params)