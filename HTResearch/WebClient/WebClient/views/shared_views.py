# stdlib imports
from django.http import HttpResponseNotFound
from django.core.context_processors import csrf
from django.shortcuts import render

# project imports
from HTResearch.Utilities.logutil import LoggingSection, get_logger

#region Globals
logger = get_logger(LoggingSection.CLIENT, __name__)
#endregion


def index(request):
    logger.info('Request made for index')
    args = {}
    args.update(csrf(request))
    return render(request, 'index/index.html', args)


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
