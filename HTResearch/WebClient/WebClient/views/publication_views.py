from urlparse import urlparse
import json

from django.shortcuts import render

from django.http import HttpResponse
from springpython.context import ApplicationContext

from HTResearch.Utilities.context import DAOContext
from HTResearch.Utilities.logutil import LoggingSection, get_logger

from HTResearch.Utilities.encoder import MongoJSONEncoder


logger = get_logger(LoggingSection.CLIENT, __name__)
ctx = ApplicationContext(DAOContext())


def search_publications(request):
    if request.method == 'GET':
        search_text = request.GET['search_text']
    else:
        search_text = ''

    publications = []

    if search_text:
        pub_dao = ctx.get_object('PublicationDAO')
        publications = pub_dao.findmany(search=search_text, num_elements=10, sort_fields=['title'])

    data = {'results': list(publications)}
    return HttpResponse(json.dumps(data, cls=MongoJSONEncoder), content_type='application/json')
