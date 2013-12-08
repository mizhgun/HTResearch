from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.hashers import make_password, check_password
from springpython.context import ApplicationContext

from HTResearch.DataAccess.dto import UserDTO
from HTResearch.DataModel.model import User
from HTResearch.Utilities.converter import DTOConverter
from HTResearch.Utilities.context import DAOContext
from HTResearch.WebClient.WebClient.models import LoginForm, SignupForm


ctx = ApplicationContext(DAOContext())


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if data['password'] != data['confirm_password']:
                return render(request, 'signup.html', {'form': form})

            password = make_password(data['password'])
            new_user = User(first_name=data['first_name'],
                            last_name=data['last_name'],
                            email=data['email'],
                            password=password,
                            background=data['background'],
                            account_type=data['account_type'],)

            if 'affiliation' in data:
                new_user.affiliation = data['affiliation']
            if 'organization' in data:
                new_user.organization = data['organization']

            user_dto = DTOConverter.to_dto(UserDTO, new_user)
            dao = ctx.get_object('UserDAO')
            dao.create_update(user_dto)

            return HttpResponseRedirect('/')
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})