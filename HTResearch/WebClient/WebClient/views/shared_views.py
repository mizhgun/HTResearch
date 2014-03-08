from datetime import datetime, timedelta
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, HttpResponseRedirect
from django.template.loader import get_template
from django.template import Context
from django.core.context_processors import csrf
from django.shortcuts import render

from mongoengine.fields import StringField, URLField, EmailField
from springpython.context import ApplicationContext
from HTResearch.Utilities.encoder import MongoJSONEncoder
from HTResearch.Utilities.context import DAOContext
from HTResearch.Utilities.logutil import LoggingSection, get_logger

logger = get_logger(LoggingSection.CLIENT, __name__)
REFRESH_COORDS_LIST = timedelta(minutes=5)


def index(request):
    logger.info('Request made for index')
    args = {}
    args.update(csrf(request))
    return render(request, 'index/index.html', args)


def dashboard(request):
    return render(request, 'dashboard/dashboard.html')


# Encodes a DTO's non-string fields to JSON
def encode_dto(dto):
    dto_type = type(dto)
    fields_dict = dto_type._fields
    string_types = (StringField, URLField, EmailField)
    json_fields = [key for key in fields_dict.iterkeys() if type(fields_dict[key]) not in string_types]
    for field in json_fields:
        dto[field] = MongoJSONEncoder().encode(dto[field])
    return dto


def heatmap_coordinates(request):
    if request.method != 'GET':
        return HttpResponseBadRequest

    coords = cache.get('organization_coords_list')
    last_update = cache.get('organization_coords_list_last_update')
    if not coords or not last_update or (datetime.utcnow() - last_update > REFRESH_COORDS_LIST):
        new_coords = []
        cache.set('organization_address_list_last_update', datetime.utcnow())
        ctx = ApplicationContext(DAOContext())
        org_dao = ctx.get_object('OrganizationDAO')
        organizations = org_dao.findmany(latlng__exists=True, latlng__ne=[])
        for org in organizations:
            new_coords.append(org.latlng)

        coords = MongoJSONEncoder().encode(new_coords)

        if len(coords) > 0:
            cache.set('organization_coords_list', coords)

    return HttpResponse(coords, content_type="application/json")


def welcome(request):
    return render(request, 'shared/welcome.html')


def unauthorized(request):
    html = render(request, 'shared/unauthorized.html')
    return HttpResponseNotFound(html, status=403)


def get_started(request):
    return render(request, 'shared/get_started.html')


def get_http_404_page(request):
    html = render(request, 'shared/404.html')
    return HttpResponseNotFound(html, status=404)


def unimplemented(request):
    return render(request, 'shared/unimplemented.html')
