# stdlib imports
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.hashers import make_password, check_password
from springpython.context import ApplicationContext
from datetime import datetime

# project imports
from HTResearch.DataAccess.dto import UserDTO, OrganizationDTO
from HTResearch.DataModel.model import User
from HTResearch.DataModel.enums import OrgTypesEnum
from HTResearch.Utilities.converter import DTOConverter
from HTResearch.Utilities.context import DAOContext
from HTResearch.Utilities.logutil import LoggingSection, LoggingUtility
from HTResearch.WebClient.WebClient.models import LoginForm, SignupForm

#region Globals
ctx = ApplicationContext(DAOContext())
SESSION_TIMEOUT = 1200
logger = LoggingUtility().get_logger(LoggingSection.CLIENT, __name__)
#endregion


def login(request):
    # if we're logged in, redirect to the index
    if 'user_id' in request.session:
        return HttpResponseRedirect('/')

    error = ''

    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            dao = ctx.get_object('UserDAO')
            user = dao.find(email=email)

            if user and check_password(password, user.password):
                logger.info('User=%s successfully logged in' % user.id)
                request.session['user_id'] = user.id
                request.session['last_modified'] = datetime.utcnow()
                request.session['name'] = user.first_name
                request.session.set_expiry(SESSION_TIMEOUT)
                return HttpResponseRedirect('/')

            error = 'No account with the provided username and password exists.'
            logger.error('User with email={0}, password={1} not found'.format(email, password))

    return render(request, 'login.html', {'form': form, 'error': error})


def logout(request):
    user_id = request.session['user_id']
    logger.info('Logging out user=%s' % user_id)
    request.session.flush()

    return HttpResponseRedirect('/')


def signup(request):
    error = ''
    form = SignupForm(request.POST or None)

    if request.method == 'POST':
        user_dao = ctx.get_object('UserDAO')

        if form.is_valid():
            data = form.cleaned_data

            password = make_password(data['password'])
            new_user = User(first_name=data['first_name'],
                            last_name=data['last_name'],
                            email=data['email'],
                            password=password,
                            background=data['background'],
                            account_type=int(data['account_type']))

            org_dao = ctx.get_object('OrganizationDAO')

            if 'org_type' in data and data['org_type']:
                new_user.org_type = int(data['org_type'])

            if 'organization' in data and data['organization']:
                existing_org = org_dao.find(name=data['organization'])
                if existing_org:
                    new_user.organization = existing_org
                else:
                    new_org = OrganizationDTO()
                    new_org.name = data['organization']
                    if new_user.org_type:
                        new_org.types.append(new_user.org_type)
                    else:
                        new_org.types.append(OrgTypesEnum.UNKNOWN)
                    new_user.organization = org_dao.create_update(new_org)

            user_dto = DTOConverter.to_dto(UserDTO, new_user)
            ret_user = user_dao.create_update(user_dto)

            request.session['name'] = new_user.first_name
            request.session['user_id'] = ret_user.id
            request.session['last_modified'] = datetime.utcnow()
            request.session.set_expiry(SESSION_TIMEOUT)

            return HttpResponseRedirect('/')

    return render(request, 'signup.html', {'form': form, 'error': error})