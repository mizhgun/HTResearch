from urlparse import urlparse
import json
from datetime import datetime, timedelta

from django.core.cache import cache
from django.shortcuts import render

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from springpython.context import ApplicationContext

from HTResearch.DataAccess.dto import URLMetadataDTO
from HTResearch.DataModel.model import URLMetadata
from HTResearch.DataModel.enums import AccountType
from HTResearch.DataModel.globals import ORG_TYPE_CHOICES
from HTResearch.Utilities.context import DAOContext
from HTResearch.Utilities.logutil import LoggingSection, get_logger
from HTResearch.Utilities.converter import DTOConverter
from HTResearch.Utilities.url_tools import UrlUtility
from HTResearch.DataModel.enums import OrgTypesEnum
from HTResearch.Utilities.encoder import MongoJSONEncoder
from HTResearch.WebClient.WebClient.views.shared_views import get_http_404_page
from HTResearch.WebClient.WebClient.models import RequestOrgForm, EditOrganizationForm

from HTResearch.Utilities.encoder import MongoJSONEncoder


logger = get_logger(LoggingSection.CLIENT, __name__)
ctx = ApplicationContext(DAOContext())

REFRESH_PARTNER_MAP = timedelta(minutes=5)

def search_organizations(request):
    user_id = request.session['user_id'] if 'user_id' in request.session else None

    if request.method == 'GET':
        search_text = request.GET['search_text']
        logger.info(
            'Search request made for organizations with search_text={0} by user={1}'.format(search_text, user_id))
    else:
        search_text = ''

    organizations = []

    if search_text:
        org_dao = ctx.get_object('OrganizationDAO')
        try:
            organizations = org_dao.findmany(search=search_text, num_elements=10,
                                             sort_fields=['valid', 'combined_weight', 'name'])
        except:
            logger.error('Exception encountered on organization search with search_text={0}'.format(search_text))
            return get_http_404_page(request)

    results = []
    for dto in organizations:
        org = dto.__dict__['_data']
        # Split organization keyword string into list of words
        org['keywords'] = (org['keywords'] or '').split()
        results.append(org)
    data = {'results': results}
    return HttpResponse(MongoJSONEncoder().encode(data), content_type="application/json")


def organization_profile(request, org_id):
    user_id = request.session['user_id'] if 'user_id' in request.session else None

    logger.info('Request made for profile of org={0} by user={1}'.format(org_id, user_id))
    org_dao = ctx.get_object('OrganizationDAO')

    try:
        org = org_dao.find(id=org_id)
    except Exception as e:
        logger.error('Exception encountered on organization lookup for org={0} by user={1}'.format(org_id, user_id))
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
    return render(request, 'organization/organization_profile.html', params)


def request_organization(request):
    if 'user_id' not in request.session:
        logger.error('Bad request made for organization seed without login')
        HttpResponseRedirect('/login')
    else:
        user_id = request.session['user_id']

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

            if not error:
                try:
                    dto = DTOConverter.to_dto(URLMetadataDTO, metadata)
                    dao.create_update(dto)
                    logger.info('Org seed with url={0} requested by user={1}'.format(url, user_id))
                    success = 'Your request has been sent successfully!'
                except:
                    error = 'Something went wrong with your request. Please try again later.'

    return render(request, 'organization/request_organization.html', {'form': form, 'success': success, 'error': error})


def edit_organization(request, org_id):
    if 'user_id' not in request.session:
        logger.error('Bad request made to edit org={0} without login'.format(org_id))
        return HttpResponseRedirect('/login')
    elif 'account_type' not in request.session or request.session['account_type'] != AccountType.CONTRIBUTOR:
        user_id = request.session['user_id']
        logger.error('Bad request made to edit org={0} by user={1}: Not a contributor account'.format(org_id, user_id))
        return HttpResponseRedirect('/')
    else:
        user_id = request.session['user_id']

    try:
        dao = ctx.get_object('OrganizationDAO')
        org = dao.find(id=org_id)
    except:
        logger.error('Exception encountered on organization lookup for org={0} by user={1}'.format(org_id, user_id))
        return get_http_404_page()

    emails = org.emails if org.emails else []
    phone_numbers = org.phone_numbers if org.phone_numbers else []
    types = org.types if org.types else []

    form = EditOrganizationForm(request.POST or None,
                                initial=_create_org_dict(org),
                                emails=emails,
                                phone_numbers=phone_numbers,
                                types=types, )
    error = ''
    success = ''

    if request.method == 'POST':
        if form.is_valid():
            data = form.cleaned_data
            new_emails = []
            new_phone_nums = []
            new_types = []

            try:
                for key, value in data.items():
                    if key.startswith('email'):
                        new_emails.append(value.strip())
                    elif key.startswith('phone'):
                        new_phone_nums.append(value.strip())
                    elif key.startswith('type'):
                        new_types.append(value.strip())
                    else:
                        setattr(org, key, value.strip()) if value else setattr(org, key, None)
            except:
                error = 'Oops! Something went wrong processing your request. Please try again later.'
                logger.error('Error occurred while updating fields for org={0} by user={1}'.format(org_id, user_id))

            if not error:
                if new_emails:
                    org.emails = [e for e in new_emails if e]
                    if org.emails:
                        org.email_key = org.emails[0]
                if new_phone_nums:
                    org.phone_numbers = [p for p in new_phone_nums if p]
                if new_types:
                    org.types = [t for t in new_types if t]

                try:
                    dao.create_update(org)
                    success = 'The organization has been updated successfully!'
                    logger.info('Org={0} updated by user={1}'.format(org_id, user_id))
                except:
                    error = 'Oops! There was an error updating the organization. Please try again later.'
                    logger.error('Error occurred saving org={0} by user={1}'.format(org_id, user_id))

    return render(request, "organization/edit_organization.html", {'form': form,
                                                      'type_choices': ORG_TYPE_CHOICES,
                                                      'org_id': org_id,
                                                      'success': success,
                                                      'error': error})


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
    return render(request, 'organization/org_rank.html')


def org_partner_map(request):
    if request.method != 'GET':
        return HttpResponseBadRequest

    pmap = cache.get('partner_map')
    last_update = cache.get('partner_map_last_update')
    if not pmap or not last_update or (datetime.utcnow() - last_update > REFRESH_PARTNER_MAP):
        new_pmap = {
            "nodes": [],
            "links": [],
            "threeps": {
                "PREVENTION": OrgTypesEnum.PREVENTION,
                "PROTECTION": OrgTypesEnum.PROTECTION,
                "PROSECUTION": OrgTypesEnum.PROSECUTION
            }
        }
        cache.set('partner_map_last_update', datetime.utcnow())
        ctx = ApplicationContext(DAOContext())
        org_dao = ctx.get_object('OrganizationDAO')
        organizations = org_dao.all('name', 'id', 'partners', 'types', 'address')
        i = 0
        for org in organizations:
            new_pmap["nodes"].append({
                "name": org.name,
                "id": str(org.id),
                "types": org.types,
                "addr": org.address
            })
            for part in org.partners:
                partner_id = str(part.id)
                for j in xrange(0, i):
                    if new_pmap["nodes"][j]["id"] == partner_id:
                        new_pmap["links"].append({
                           "source": i,
                           "target": j
                        })

            i += 1



        pmap = MongoJSONEncoder().encode(new_pmap)

        cache.set('partner_map', pmap)

    return HttpResponse(pmap, content_type="application/json")


def partner_map_demo(request):
    return render(request, 'data-vis/partner-map-demo.html')


def _create_org_dict(org):
    org_dict = {
        'name': org.name if org.name else "",
        'address': org.address if org.address else "",
        'organization_url': "http://" + org.organization_url if org.organization_url else "",
        'keywords': org.keywords.replace(' ', ', ') if org.keywords else "",
        'facebook': org.facebook if org.facebook else "",
        'twitter': org.twitter if org.twitter else "",
        'invalid': not org.valid
    }
    return org_dict
