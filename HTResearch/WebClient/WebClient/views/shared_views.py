# stdlib imports
from django.http import HttpResponseNotFound, HttpResponseForbidden, HttpResponseServerError
from django.core.context_processors import csrf
from django.shortcuts import render

# project imports
from HTResearch.Utilities.logutil import LoggingSection, get_logger

#region Globals
logger = get_logger(LoggingSection.CLIENT, __name__)
#endregion


def index(request):
    """Sends a request to the Index page."""
    logger.info('Request made for index')
    args = {}
    args.update(csrf(request))
    return render(request, 'index/index.html', args)


def welcome(request):
    """Sends a request to the Welcome page."""
    return render(request, 'shared/welcome.html')


def statistics(request):
    return render(request, 'statistics/statistics.html')


def unauthorized(request):
    """Sends a request to the Unauthorized page."""
    html = render(request, 'shared/unauthorized.html')
    return HttpResponseForbidden(html)


def get_started(request):
    """Sends a request to the Get Stated page."""
    return render(request, 'shared/get_started.html')


def not_found(request):
    """Sends a request to the 404 page."""
    html = render(request, 'shared/not_found.html')
    return HttpResponseNotFound(html)


def server_error(request):
    html = render(request, 'shared/server_error.html')
    return HttpResponseServerError(html)


def about(request):
    """Sends a request to the About page."""
    return render(request, 'shared/about.html')