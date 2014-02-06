from django.shortcuts import render
from springpython.context import ApplicationContext
from HTResearch.Utilities.context import DAOContext
from HTResearch.Utilities.logutil import LoggingSection, get_logger
from HTResearch.WebClient.WebClient.views.shared_views import encode_dto, get_http_404_page
from HTResearch.Utilities.encoder import MongoJSONEncoder
from django.http import HttpResponse
import json

logger = get_logger(LoggingSection.CLIENT, __name__)
ctx = ApplicationContext(DAOContext())


def contact_profile(request, contact_id):
    logger.info('Request made for profile of contact_id=%s' % contact_id)
    contact_dao = ctx.get_object('ContactDAO')

    try:
        contact = contact_dao.find(id=contact_id)
    except Exception as e:
        logger.error('Exception encountered on contact lookup for contact_id=%s' % contact_id)
        print e.message
        return get_http_404_page(request)

    org_url = '/organization/' + str(contact.organization.id) if contact.organization else ''

    params = {"contact": contact,
              "org_url": org_url}

    return render(request, 'contact_profile.html', params)


def search_contacts(request):
    if request.method == 'GET':
        search_text = request.GET['search_text']
    else:
        search_text = ''

    contacts = []

    if search_text:
        contact_dao = ctx.get_object('ContactDAO')

        contacts = contact_dao.findmany(search=search_text,
                                        num_elements=10,
                                        sort_fields=['last_name', 'first_name'])

    data = {'results': map(lambda x: x.__dict__['_data'], contacts)}
    return HttpResponse(MongoJSONEncoder().encode(data), 'application/json')