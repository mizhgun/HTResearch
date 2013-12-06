from urlparse import urlparse
from django.shortcuts import render_to_response
from springpython.context import ApplicationContext
from HTResearch.Utilities.context import DAOContext
from HTResearch.Utilities.logutil import LoggingSection, LoggingUtility
from HTResearch.WebClient.WebClient.views.shared_views import encode_dto, get_http_404_page

logger = LoggingUtility().get_logger(LoggingSection.CLIENT, __name__)
ctx = ApplicationContext(DAOContext())


def search_organizations(request):

    if request.method == 'GET':
        search_text = request.GET['search_text']
        logger.info('Search request made with search_text=%s' % search_text)
    else:
        search_text = ''

    organizations = []

    if search_text:
        org_dao = ctx.get_object('OrganizationDAO')

        organizations = org_dao.text_search(search_text, 10, 'name')

        for dto in organizations:
            encode_dto(dto)

    params = {'organizations': organizations}
    return render_to_response('org_search_results.html', params)


def organization_profile(request, org_id):
    logger.info('Request made for profile of org_id=%s' % org_id)
    org_dao = ctx.get_object('OrganizationDAO')

    try:
        org = org_dao.find(id=org_id)
    except Exception as e:
        logger.error('Exception encountered on organization lookup for org_id=%s' % org_id)
        print e.message
        return get_http_404_page(request)

    params = {"organization": org}
    return render_to_response('organization_profile_template.html', params)


def get_org_rank_rows(request):
    start = int(request.GET['start'])
    end = int(request.GET['end'])
    sort = request.GET['sort']

    org_dao = ctx.get_object('OrganizationDAO')
    organizations = list(org_dao.findmany(start=start, end=end, sort_fields=sort))

    # add netloc to urls if needed
    for org in organizations:
        if org.organization_url is not None:
            netloc = urlparse(org.organization_url).netloc
            if netloc == "":
                org.organization_url = "//" + org.organization_url


    params = {'organizations': organizations}
    return render_to_response('org_rank_row.html', params)


def org_rank(request, sort_method=''):
    return render_to_response('org_rank.html')