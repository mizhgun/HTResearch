from urlparse import urlparse
import json

from django.shortcuts import render

from django.http import HttpResponse
from springpython.context import ApplicationContext

from HTResearch.Utilities.context import DAOContext
from HTResearch.Utilities.logutil import LoggingSection, get_logger
from HTResearch.WebClient.WebClient.views.shared_views import get_http_404_page

from HTResearch.Utilities.encoder import MongoJSONEncoder

from datetime import *


logger = get_logger(LoggingSection.CLIENT, __name__)
ctx = ApplicationContext(DAOContext())


def pub_count(request):
    user_id = request.session['user_id'] if 'user_id' in request.session else None

    logger.info('Publication count request made by user {0}'.format(user_id))

    pub_dao = ctx.get_object('PublicationDAO')

    count = ''
    try:
        count = pub_dao.count()
    except:
        logger.error('Exception encountered on publication count by user={0}'.format(user_id))

    data = {
        'count': count
    }

    return HttpResponse(data)


def search_publications(request):
    user_id = request.session['user_id'] if 'user_id' in request.session else None

    if request.method == 'GET':
        search_text = request.GET['search_text']
        logger.info('Search request made for publications with search_text={0} by user {1}'.format(search_text, user_id))
    else:
        search_text = ''

    publications = []

    if search_text:
        pub_dao = ctx.get_object('PublicationDAO')
        try:
            publications = pub_dao.findmany(search=search_text, num_elements=10, sort_fields=['valid', 'title'])
        except Exception:
            logger.error('Exception encountered on publication search with search_text={0}'.format(search_text))
            return get_http_404_page(request)

    results = []
    for dto in publications:
        pub = dto.__dict__['_data']
        # Change the datetime to make it readable in the modal
        pub['publication_date'] = str(pub['publication_date'].year)
        results.append(pub)

    data = {'results': results}
    return HttpResponse(MongoJSONEncoder().encode(data), content_type='application/json')
