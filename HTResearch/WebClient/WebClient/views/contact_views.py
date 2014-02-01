from django.shortcuts import render
from springpython.context import ApplicationContext
from django.http import HttpResponse
import json

from HTResearch.Utilities.context import DAOContext
from HTResearch.Utilities.logutil import LoggingSection, get_logger
from HTResearch.WebClient.WebClient.views.shared_views import encode_dto, get_http_404_page
from HTResearch.WebClient.WebClient.models import EditContactForm, EditContactModel
from HTResearch.Utilities.encoder import MongoJSONEncoder

logger = get_logger(LoggingSection.CLIENT, __name__)
ctx = ApplicationContext(DAOContext())


def contact_profile(request, contact_id):
    logger.info('Request made for profile of contact_id=%s' % contact_id)
    contact_dao = ctx.get_object('ContactDAO')

    try:
        contact = contact_dao.find(id=contact_id)
    except Exception:
        logger.error('Exception encountered on contact lookup for contact_id=%s' % contact_id)
        return get_http_404_page(request)

    org_url = '/organization/' + str(contact.organization.id) if contact.organization else ''

    params = {"contact": contact,
              "org_url": org_url}

    return render(request, 'contact_profile.html', params)


def search_contacts(request):
    if request.method == 'GET':
        search_text = request.GET['search_text']
    else:
        search_text = ''

    contacts = []

    if search_text:
        contact_dao = ctx.get_object('ContactDAO')

        contacts = contact_dao.text_search(text=search_text,
                                           fields=['first_name', 'last_name', 'position', ],
                                           num_elements=10,
                                           sort_fields=['last_name'])

    data = {'results': map(lambda x: x.__dict__['_data'], contacts)}
    return HttpResponse(MongoJSONEncoder().encode(data), 'application/json')


def edit_contact(request, contact_id):
    contact_dao = ctx.get_object('ContactDAO')

    error = ''
    success = ''

    try:
        contact = contact_dao.find(id=contact_id)
    except Exception:
        logger.error('Exception encountered on contact lookup for contact_id=%s' % contact_id)
        return get_http_404_page(request)

    form = EditContactForm(request.POST or None)
    model = EditContactModel(contact=contact)

    if request.method == 'POST':
        valid_edit = True

        if form.is_valid():
            data = form.cleaned_data
            model = EditContactModel(form=data)

            if 'first_name' in data:
                contact.first_name = data['first_name']
            if 'last_name' in data:
                contact.last_name = data['last_name']
            if 'email' in data:
                contact.email = data['email']
            if 'phone' in data:
                contact.phone = data['phone']
            if 'position' in data:
                contact.position = data['position']
            if 'invalid' in data:
                contact.valid = not data['invalid']

            if valid_edit:
                try:
                    contact_dao.create_update(contact)
                    success = 'The contact has been updated successfully!'
                except:
                    error = 'Oops! There was an error updating the contact. Please try again soon.'

    return render(request, 'edit_contact.html', {'form': form, 'model': model, 'success': success, 'error': error})