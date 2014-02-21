# stdlib imports
from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.hashers import make_password, check_password
from email.mime.text import MIMEText
import smtplib
from springpython.context import ApplicationContext

# project imports
from HTResearch.DataAccess.dto import UserDTO, OrganizationDTO
from HTResearch.DataModel.model import User
from HTResearch.DataModel.enums import OrgTypesEnum
from HTResearch.Utilities.config import get_config_value
from HTResearch.Utilities.converter import DTOConverter
from HTResearch.Utilities.context import DAOContext
from HTResearch.Utilities.logutil import LoggingSection, get_logger
from HTResearch.WebClient.WebClient.models import LoginForm, SignupForm, InviteForm

#region Globals
ctx = ApplicationContext(DAOContext())
SESSION_TIMEOUT = 1200
logger = get_logger(LoggingSection.CLIENT, __name__)
#endregion


def login(request):
    # if we're logged in, redirect to the index
    if 'user_id' in request.session:
        user_id = request.session['user_id']
        logger.error('Bad request for login made by user={0}'.format(user_id))
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
                logger.info('User={0} successfully logged in'.format(user.id))
                request.session['user_id'] = user.id
                request.session['last_modified'] = datetime.utcnow()
                request.session['name'] = user.first_name
                request.session['account_type'] = user.account_type
                request.session.set_expiry(SESSION_TIMEOUT)
                return HttpResponseRedirect('/')

            error = 'No account with the provided username and password exists.'
            logger.error('User with email={0}, password={1} not found'.format(email, password))

    return render(request, 'login.html', {'form': form, 'error': error})


def logout(request):
    if 'user_id' not in request.session:
        logger.error('Bad request made for logout without login')
        return HttpResponseRedirect('/')

    user_id = request.session['user_id']
    logger.info('Logging out user={0}'.format(user_id))
    request.session.flush()

    return HttpResponseRedirect('/')


def signup(request):
    if 'user_id' in request.session:
        user_id = request.session['user_id']
        logger.error('Bad request for signup made by user={0}'.format(user_id))
        return HttpResponseRedirect('/')

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

            try:
                user_dto = DTOConverter.to_dto(UserDTO, new_user)
                ret_user = user_dao.create_update(user_dto)
                request.session['name'] = new_user.first_name
                request.session['user_id'] = ret_user.id
                request.session['last_modified'] = datetime.utcnow()
                request.session['account_type'] = ret_user.account_type
                request.session.set_expiry(SESSION_TIMEOUT)
                return HttpResponseRedirect('/')
            except:
                logger.error('Error occurred during signup')
                error = 'Oops! We had a little trouble signing you up. Please try again later.'

    return render(request, 'signup.html', {'form': form, 'error': error})


def send_invite(request):
    if 'user_id' not in request.session:
        logger.error('Request made for send_invite without login')
        return HttpResponseRedirect('/login')
    else:
        user_id = request.session['user_id']

    form = InviteForm(request.POST or None)
    error = ''
    success = ''

    if request.method == 'POST':
        if form.is_valid():
            to = form.cleaned_data['email']

            logger.info('Request made to invite email={0} by user={1}'.format(
                to, user_id
            ))

            if 'message' in form.cleaned_data:
                message = form.cleaned_data['message']

            invitation = "Hello! You've just been invited to UNL HT Research by {0}."\
                .format(request.session['name'])

            if message:
                invitation += " They've included a message below:\n\n{0}".format(message)

            mail = MIMEText(invitation)
            mail['Subject'] = 'Come Join UNL HT Research!'
            mail['From'] = 'jdegner0129@gmail.com'
            mail['To'] = to

            username = get_config_value("MAIL", "username")
            password = get_config_value("MAIL", "password")

            try:
                if not (username and password):
                    raise Exception

                s = smtplib.SMTP('smtp.gmail.com:587')
                s.starttls()
                s.login(username, password)
                s.sendmail('jdegner0129@gmail.com', [to], mail.as_string())
                s.quit()
                success = 'Your invite has been sent successfully!'
                logger.info('Invite sent to email={0} by user={1}'.format(
                    to, user_id
                ))
            except:
                logger.error('Invite request by user={0} to email={1} failed.'.format(
                    user_id, to
                ))
                error = 'Oops! It looks like something went wrong. Please try again later.'

    return render(request, 'send_invite.html', {'form': form, 'error': error, 'success': success})