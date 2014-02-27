from django.shortcuts import render
from springpython.context import ApplicationContext
from django.http import HttpResponse, HttpResponseRedirect

from HTResearch.DataModel.enums import AccountType
from HTResearch.Utilities.context import DAOContext
from HTResearch.Utilities.logutil import LoggingSection, get_logger
from HTResearch.WebClient.WebClient.views.shared_views import get_http_404_page
from HTResearch.WebClient.WebClient.models import EditContactForm
from HTResearch.Utilities.encoder import MongoJSONEncoder

logger = get_logger(LoggingSection.CLIENT, __name__)
ctx = ApplicationContext(DAOContext())


def contact_profile(request, contact_id):
    user_id = request.session['user_id'] if 'user_id' in request.session else None

    logger.info('Request made for profile of contact={0} by user={1}'.format(contact_id, user_id))
    contact_dao = ctx.get_object('ContactDAO')

    try:
        contact = contact_dao.find(id=contact_id)
    except Exception:
        logger.error('Exception encountered on contact lookup for contact={0}'.format(contact_id))
        return get_http_404_page(request)

    org_url = '/organization/' + str(contact.organization.id) if contact.organization else ''

    params = {"contact": contact,
              "org_url": org_url}

    return render(request, 'contact_profile.html', params)


def search_contacts(request):
    user_id = request.session['user_id'] if 'user_id' in request.session else None

    if request.method == 'GET':
        search_text = request.GET['search_text']
        logger.info('Search request made for contacts with search_text={0} by user {1}'.format(search_text, user_id))
    else:
        search_text = ''

    contacts = []

    if search_text:
        contact_dao = ctx.get_object('ContactDAO')
        try:
            contacts = contact_dao.findmany(search=search_text,
                                            num_elements=10,
                                            sort_fields=['valid', 'last_name', 'first_name'])
        except Exception:
            logger.error('Exception encountered on contact search with search_text={0}'.format(search_text))
            return get_http_404_page(request)

    data = {'results': map(lambda x: x.__dict__['_data'], contacts)}
    return HttpResponse(MongoJSONEncoder().encode(data), 'application/json')


def edit_contact(request, contact_id):
    if 'user_id' not in request.session:
        return HttpResponseRedirect('/login')
    elif 'account_type' not in request.session or request.session['account_type'] != AccountType.CONTRIBUTOR:
        return HttpResponseRedirect('/')
    else:
        user_id = request.session['user_id']

    contact_dao = ctx.get_object('ContactDAO')

    error = ''
    success = ''

    try:
        contact = contact_dao.find(id=contact_id)
    except Exception:
        logger.error('Exception encountered on contact lookup for contact={0} by user={1}'.format(contact_id, user_id))
        return get_http_404_page(request)

    phones = contact.phones if contact.phones else []

    form = EditContactForm(request.POST or None,
                           initial=_create_contact_dict(contact),
                           phones=phones)

    if request.method == 'POST':
        if form.is_valid():
            data = form.cleaned_data
            new_phones = []

            if 'invalid' in data:
                contact.valid = not data['invalid']

            try:
                for key, value in data.items():
                    if key.startswith('phone'):
                        new_phones.append(value.strip())
                    else:
                        setattr(contact, key, value.strip()) if value else setattr(contact, key, None)
            except:
                error = 'Oops! Something went wrong processing your request. Please try again later.'
                logger.error('Error occurred while updating fields for contact={0} by user={1}'.format(contact_id, user_id))

            if not error:
                if new_phones:
                    contact.phones = [p for p in new_phones if p]

                try:
                    contact_dao.create_update(contact)
                    success = 'The contact has been updated successfully!'
                    logger.info('Contact={0} updated by user={1}'.format(contact_id, user_id))
                except:
                    error = 'Oops! There was an error updating the contact. Please try again soon.'

    return render(request, 'edit_contact.html', {'form': form, 'contact_id': contact_id,
                                                 'success': success, 'error': error})


def _create_contact_dict(contact):
    contact_dict = {'first_name': contact.first_name if contact.first_name else "",
                    'last_name': contact.last_name if contact.last_name else "",
                    'email': contact.email if contact.email else "",
                    'position': contact.position if contact.position else "", 'invalid': not contact.valid}
    return contact_dict
