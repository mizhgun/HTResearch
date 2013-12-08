# stdlib imports
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.hashers import make_password, check_password
from springpython.context import ApplicationContext

# project imports
from HTResearch.DataAccess.dto import UserDTO, OrganizationDTO
from HTResearch.DataModel.model import User
from HTResearch.Utilities.converter import DTOConverter
from HTResearch.Utilities.context import DAOContext
from HTResearch.WebClient.WebClient.models import LoginForm, SignupForm


ctx = ApplicationContext(DAOContext())


def login(request):
    msg = ''

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            dao = ctx.get_object('UserDAO')
            user = dao.find(email=email)
            if user and check_password(password, user.password):
                return HttpResponseRedirect('/')

            msg = 'No account with the provided username and password exists.'
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form, 'msg': msg})


def signup(request):
    msg = ''

    if request.method == 'POST':
        form = SignupForm(request.POST)
        user_dao = ctx.get_object('UserDAO')

        if form.is_valid():
            data = form.cleaned_data

            if data['password'] != data['confirm_password']:
                msg = 'Please make sure your passwords match.'
            elif user_dao.find(email=data['email']):
                msg = 'An account with that email already exists.'
            else:
                password = make_password(data['password'])
                new_user = User(first_name=data['first_name'],
                                last_name=data['last_name'],
                                email=data['email'],
                                password=password,
                                background=data['background'],
                                account_type=int(data['account_type']),)

                org_dao = ctx.get_object('OrganizationDAO')

                if 'affiliation' in data and data['affiliation']:
                    new_user.affiliation = int(data['affiliation'])

                if 'organization' in data and data['organization']:
                    existing_org = org_dao.find(name=data['organization'])
                    if existing_org:
                        new_user.organization = existing_org
                    else:
                        new_org = OrganizationDTO()
                        new_org.name = data['organization']
                        new_user.organization = org_dao.create_update(new_org)

                user_dto = DTOConverter.to_dto(UserDTO, new_user)
                user_dao.create_update(user_dto)

            return HttpResponseRedirect('/')
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form, 'msg': msg})