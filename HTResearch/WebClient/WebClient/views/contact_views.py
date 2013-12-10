from django.shortcuts import render_to_response
from springpython.context import ApplicationContext
from HTResearch.Utilities.context import DAOContext
from HTResearch.Utilities.logutil import LoggingSection, LoggingUtility
from HTResearch.WebClient.WebClient.views.shared_views import encode_dto, get_http_404_page

logger = LoggingUtility().get_logger(LoggingSection.CLIENT, __name__)
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

    org_url = '/organization/'+contact.organization.id if contact.organization else ''

    params = {"contact": contact,
              "org_url": org_url}

    return render_to_response('contact_profile_template.html', params)


def search_contacts(request):

    if request.method == 'GET':
        search_text = request.GET['search_text']
    else:
        search_text = ''

    contacts = []

    if search_text:
        ctx = ApplicationContext(DAOContext())
        contact_dao = ctx.get_object('ContactDAO')

        contacts = contact_dao.text_search(search_text, 10, sort_fields=['last_name'])

        for dto in contacts:
            encode_dto(dto)

    params = {'contacts': contacts}
    return render_to_response('contact_search_results.html', params)