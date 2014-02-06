from urlparse import urlparse
import json

from django.shortcuts import render

from django.http import HttpResponse, HttpResponseRedirect
from springpython.context import ApplicationContext

from HTResearch.DataAccess.dto import URLMetadataDTO
from HTResearch.DataModel.model import URLMetadata
from HTResearch.Utilities.context import DAOContext
from HTResearch.Utilities.logutil import LoggingSection, get_logger
from HTResearch.Utilities.converter import DTOConverter
from HTResearch.Utilities.url_tools import UrlUtility
from HTResearch.DataModel.enums import OrgTypesEnum
from HTResearch.Utilities.encoder import MongoJSONEncoder
from HTResearch.WebClient.WebClient.views.shared_views import encode_dto, get_http_404_page
from HTResearch.WebClient.WebClient.models import RequestOrgForm

from HTResearch.Utilities.encoder import MongoJSONEncoder


logger = get_logger(LoggingSection.CLIENT, __name__)
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
        organizations = org_dao.findmany(search=search_text, num_elements=10, sort_fields=['name'])

    results = []
    for dto in organizations:
        org = dto.__dict__['_data']
        # Split organization keyword string into list of words
        org['keywords'] = (org['keywords'] or '').split()
        results.append(org)
    data = {'results': results}
    return HttpResponse(MongoJSONEncoder().encode(data), content_type="application/json")


def organization_profile(request, org_id):
    logger.info('Request made for profile of org_id=%s' % org_id)
    org_dao = ctx.get_object('OrganizationDAO')

    try:
        org = org_dao.find(id=org_id)
    except Exception as e:
        logger.error('Exception encountered on organization lookup for org_id=%s' % org_id)
        print e.message
        return get_http_404_page(request)

    scheme = ""
    if org.organization_url is not None:
        scheme = urlparse(org.organization_url).scheme

    type_nums = org['types']
    org_types = []
    for org_type in type_nums:
        org_types.append(OrgTypesEnum.reverse_mapping[org_type].title())

    params = {"organization": org,
              "scheme": scheme,
              "types": org_types,
              }
    return render(request, 'organization_profile.html', params)


def request_organization(request):
    if 'user_id' not in request.session:
        HttpResponseRedirect('/login')

    form = RequestOrgForm(request.POST or None)
    error = ''
    success = ''

    if request.method == 'POST':
        if form.is_valid():
            url = form.cleaned_data['url']
            dao = ctx.get_object('URLMetadataDAO')

            try:
                metadata = URLMetadata(url=url, domain=UrlUtility.get_domain(url))
            except ValueError:
                error = "Oops! We don't recognize that domain. Please try another."

            try:
                dto = DTOConverter.to_dto(URLMetadataDTO, metadata)
                dao.create_update(dto)
            except:
                error = 'Something went wrong with your request. Please try again later.'

            success = 'Your request has been sent successfully!'

    return render(request, 'request_organization.html', {'form': form, 'success': success, 'error': error})


def get_org_keywords(request):
    if request.method == 'GET':
        org_id = request.GET['org_id']
    else:
        org_id = ''

    org_dao = ctx.get_object('OrganizationDAO')
    org = org_dao.find(id=org_id)
    keywords = org.keywords.split(' ')
    #Commenting out instead of deleting for demo purposes
    #If keywords aren't in the database, you should uncomment this and use Bombay Teen Challenge
    #org.keywords = {'access': 32, 'addicts': 51, 'afraid': 32, 'allows': 32, 'ambedkar': 32,
    #                'announced': 32, 'ashes': 32, 'bandra': 32, 'beauty': 32, 'began': 32,
    #                'betrayed': 32, 'blog': 32, 'blogs': 32, 'bombay': 384, 'bound': 32,
    #                'btc': 64, 'care': 51, 'challenge': 358, 'children': 64, 'contact': 64,
    #                'donate': 64, 'drug': 64, 'education': 89, 'education.': 39, 'gift': 64,
    #                'health': 96, 'homes': 83, 'india': 64, 'light': 64, 'live': 64, 'lives': 96,
    #                'men': 53, 'mumbai': 102, 'music': 83, 'office': 38, 'out.': 39, 'programs': 53,
    #                'read': 96, 'red': 64, 'rescued': 83, 'safe': 53, 'seek': 160, 'streets': 64,
    #                'teen': 384, 'tel': 34, 'training': 51, 'trust': 64, 'vocational': 96, 'women': 112}
    return HttpResponse(json.dumps(keywords), mimetype='application/json')


def get_org_rank_rows(request):
    start = int(request.GET['start'])
    end = int(request.GET['end'])
    page_size = end - start + 1
    if 'search' in request.GET:
        search = request.GET['search']
    else:
        search = None
    if 'sort' in request.GET:
        sort = request.GET['sort']
    else:
        sort = ()

    org_dao = ctx.get_object('OrganizationDAO')
    organizations = list(org_dao.findmany(start=start, end=end, sort_fields=[sort], search=search))
    records = org_dao.count(search)

    # add netloc to urls if needed
    for org in organizations:
        if org.organization_url is not None:
            netloc = urlparse(org.organization_url).netloc
            if netloc == "":
                org.organization_url = "//" + org.organization_url

    obj = {
        'data': organizations,
        'records': records
    }

    return HttpResponse(MongoJSONEncoder().encode(obj), content_type="application/text")


def org_rank(request, sort_method=''):
    return render(request, 'org_rank.html')