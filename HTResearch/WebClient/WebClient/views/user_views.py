# stdlib imports
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
from HTResearch.WebClient.WebClient.views.shared_views import unauthorized
from HTResearch.WebClient.WebClient.models import LoginForm, SignupForm, InviteForm, ManageForm

#region Globals
ctx = ApplicationContext(DAOContext())
SESSION_TIMEOUT = 1200
logger = get_logger(LoggingSection.CLIENT, __name__)
#endregion


def login(request):
    """
    Sends a request to the Login page.

    Returns:
        A rendered page of the Login form if the user is not logged in already.
    """
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
                request.session['user_id'] = str(user.id)
                request.session['first_name'] = str(user.first_name)
                request.session['last_name'] = str(user.last_name)
                request.session['account_type'] = user.account_type
                request.session.set_expiry(SESSION_TIMEOUT)
                route = request.session['next'] if 'next' in request.session else '/'
                return HttpResponseRedirect(route)

            error = 'No account with the provided username and password exists.'
            logger.error('User with email={0}, password={1} not found'.format(email, password))

    if 'HTTP_REFERER' in request.META and ('next' not in request.session or request.path != request.session['next']):
        request.session['next'] = request.META['HTTP_REFERER']
    return render(request, 'user/login.html', {'form': form, 'error': error})


def logout(request):
    """Logs the user out. Sends the user to the index page."""
    if 'user_id' not in request.session:
        logger.error('Bad request made for logout without login')
        return unauthorized(request)

    user_id = request.session['user_id']
    logger.info('Logging out user={0}'.format(user_id))
    request.session.flush()

    return HttpResponseRedirect('/')


def signup(request):
    """
    Sends a request to the Signup page.

    Returns:
        A rendered page of the Signup form if the user is not logged in already.
    """
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
                request.session['name'] = str(new_user.first_name) + ' ' + str(new_user.last_name)
                request.session['user_id'] = str(ret_user.id)
                request.session['account_type'] = str(ret_user.account_type)
                request.session.set_expiry(SESSION_TIMEOUT)
                return HttpResponseRedirect('/')
            except:
                logger.error('Error occurred during signup')
                error = 'Oops! We had a little trouble signing you up. Please try again later.'

    return render(request, 'user/signup.html', {'form': form, 'error': error})


def manage_account(request):
    """
    Sends a request to the Account Preferences page.

    Returns:
        A rendered page with editable account settings if the user is logged in.
    """
    if 'user_id' not in request.session:
        logger.error('Request made for account-preferences without login')
        return HttpResponseRedirect('/login')

    user_id = request.session['user_id']
    user_dao = ctx.get_object('UserDAO')
    user = user_dao.find(id=user_id)
    user_dict = _create_user_dict(user)
    user_dict['user_id'] = str(user_id)
    form = ManageForm(
        request.POST or None,
        initial=user_dict
    )
    error = ''
    success = ''
    if request.method == 'POST':
        if form.is_valid():
            data = form.cleaned_data
            password = data['password']
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.account_type = int(data['account_type'])
            user.background = data['background']
            user.email = data['email']
            if 'org_type' in data and data['org_type']:
                user.org_type = int(data['org_type'])
            if password:
                user.password = make_password(password)
            org_dao = ctx.get_object('OrganizationDAO')
            if 'organization' in data and data['organization']:
                existing_org = org_dao.find(name=data['organization'])
                if existing_org:
                    user.organization = existing_org
                else:
                    new_org = OrganizationDTO()
                    new_org.name = data['organization']
                    if user.org_type:
                        new_org.types.append(user.org_type)
                    else:
                        new_org.types.append(OrgTypesEnum.UNKNOWN)
                    user.organization = org_dao.create_update(new_org)
            try:
                ret_user = user_dao.create_update(user)
                success = 'Account settings changed successfully'
                request.session['name'] = ret_user.first_name + ' ' + ret_user.last_name
                request.session['account_type'] = ret_user.account_type
            except:
                logger.error('Error occurred during account update for user={0}'.format(user_id))
                error = 'Oops! We had a little trouble updating your account. Please try again later.'
    return render(request, 'user/manage.html', {'form': form, 'error': error, 'success': success})


def send_invite(request):
    """
    Sends a request to the Send Invite page.

    Returns:
        A rendered page with the Send Invite form if the user is logged in.
    """
    if 'user_id' not in request.session:
        logger.error('Request made for send_invite without login')
        return unauthorized(request)
    else:
        user_id = request.session['user_id']

    form = InviteForm(request.POST or None)
    error = ''
    success = ''

    if request.method == 'POST':
        if form.is_valid():
            to = form.cleaned_data['email']
            name = "{0} {1}".format(request.session['first_name'], request.session['last_name'])

            logger.info('Request made to invite email={0} by user={1}'.format(
                to, user_id
            ))

            if 'message' in form.cleaned_data:
                message = form.cleaned_data['message']

            invitation = "Hello!<br><br>{0} has invited you to be a part of the Anti-Trafficking Atlas (ATA), a " \
                         "website that aggregates anti-trafficking information, such as organizations, people, news, " \
                         "and publications by programmatically pulling data from the web. This site allows " \
                         "researchers, advocates, and volunteers to search for places to help and people with which " \
                         "to collaborate. If you sign up for an account, you can also aid in making sure the website " \
                         "has complete and correct information. Help us make the anti-trafficking efforts of the " \
                         "world easy to find. Go to <a href=\"unlaht.cloudapp.net\">unlaht.cloudapp.net</a> to sign " \
                         "up!<br><br>" \
                         .format(name)

            if message:
                invitation += "{0} says: \"{1}\"<br><br>".format(name, message)

            invitation += "Thank you,<br><br>The ATA Team"

            mail = MIMEText(invitation, 'html')
            mail['Subject'] = 'Come join the Anti-Trafficking Atlas!'
            mail['From'] = 'ATA'
            mail['To'] = to

            username = get_config_value("MAIL", "username")
            password = get_config_value("MAIL", "password")
            server = get_config_value("MAIL", "server")
            port = get_config_value("MAIL", "port")

            try:
                if not (username and password):
                    raise Exception

                s = smtplib.SMTP_SSL('{0}:{1}'.format(
                    server, port
                ))
                s.login(username, password)
                s.sendmail('ATA@cse.unl.edu', [to], mail.as_string())
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
    return render(request, 'user/send_invite.html', {'form': form, 'error': error, 'success': success})


def _create_user_dict(user):
    """
    Helper function to convert a User to a dictionary.

    Arguments:
        user (User): The user that is being converted.

    Returns:
        A { string : string } dictionary of User fields.
    """
    user_dict = {
        'first_name': user.first_name or "",
        'last_name': user.last_name or "",
        'email': user.email or "",
        'account_type': user.account_type if user.account_type is not None else "",
        'org_type': user.org_type if user.org_type is not None else "",
        'organization': user.organization.name if user.organization else "",
        'background': user.background or ""
    }
    return user_dict