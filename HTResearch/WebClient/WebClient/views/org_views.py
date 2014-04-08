# stdlib imports
from urlparse import urlparse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from springpython.context import ApplicationContext
import re

# project imports
from HTResearch.DataAccess.dto import URLMetadataDTO
from HTResearch.DataModel.model import URLMetadata
from HTResearch.DataModel.enums import AccountType
from HTResearch.DataModel.globals import ORG_TYPE_CHOICES
from HTResearch.Utilities.context import DAOContext
from HTResearch.Utilities.logutil import LoggingSection, get_logger
from HTResearch.Utilities.converter import DTOConverter
from HTResearch.Utilities.url_tools import UrlUtility
from HTResearch.DataModel.enums import OrgTypesEnum
from HTResearch.WebClient.WebClient.views.shared_views import get_http_404_page
from HTResearch.WebClient.WebClient.models import RequestOrgForm, EditOrganizationForm

#region Globals
logger = get_logger(LoggingSection.CLIENT, __name__)
ctx = ApplicationContext(DAOContext())
#endregion


def organization_profile(request, org_id):
    """
    Sends a request to the Organization Profile page and retrieves Organization information for the profile.

    Arguments:
        org_id (string): The id of the organization.

    Returns:
        A rendered page of the Organization Profile.
    """
    user_id = request.session['user_id'] if 'user_id' in request.session else None
    account_type = request.session['account_type'] if 'account_type' in request.session else None

    logger.info('Request made for profile of org={0} by user={1}'.format(org_id, user_id))
    org_dao = ctx.get_object('OrganizationDAO')

    try:
        org = org_dao.find(id=org_id)
    except:
        logger.error('Exception encountered on organization lookup for org={0} by user={1}'.format(org_id, user_id))
        return get_http_404_page(request)

    scheme = ""
    if org.organization_url is not None:
        scheme = urlparse(org.organization_url).scheme

    type_nums = org['types']
    org_types = []
    for org_type in type_nums:
        org_types.append(OrgTypesEnum.reverse_mapping[org_type].title())

    facebook_str = None
    if org.facebook:
        fb_regex = re.compile('(?:(?:http|https):\/\/)?(?:www.)?'
                                'facebook.com\/(?:(?:\w)*#!\/)?'
                                '(?:pages\/)?(?:[?\w\-]*\/)?'
                                '(?:profile.php\?id=(?=\d.*))?([\w\-]*)?')
        fb_match = fb_regex.match(org.facebook)
        facebook_str = fb_match.group(1) if fb_match else None

    twitter_str = "@" + org.twitter.split('/')[-1] if org.twitter else None

    can_edit = account_type == AccountType.CONTRIBUTOR

    params = {"organization": org,
              "scheme": scheme,
              "types": org_types,
              "facebook": facebook_str,
              "twitter": twitter_str,
              "can_edit": can_edit,
              }
    return render(request, 'organization/organization_profile.html', params)


def request_organization(request):
    """
    Sends a request to the Request Organization page if the user is logged in.

    Returns:
        A rendered page containing the Request Organization form.
    """
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
    """
    Sends a request to the Edit Organization page if the user is logged in and a contributor account type.

    Arguments:
        org_id (string): The id of the organization that is being edited.

    Returns:
        A rendered page containing the Edit Organization form.
    """
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


def org_rank(request, sort_method=''):
    """
    Sends a request to the org rank page, or the View All Organizations page.

    Arguments:
        sort_method (string): How the organizations should be sorted on the page.

    Returns:
        A rendered page to the org rank page
    """
    return render(request, 'organization/org_rank.html')


def partner_map_demo(request):
    """Demo of the partner map."""
    return render(request, 'data-vis/partner-map-demo.html')


def _create_org_dict(org):
    """
    Helper function to convert a Organization to a dictionary.

    Arguments:
        org (Organization): The organization that is being converted.

    Returns:
        A { string : string } dictionary of Organization fields.
    """
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
