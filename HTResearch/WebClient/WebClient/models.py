# stdlib imports
from django import forms
from django.core.exceptions import ValidationError
from springpython.context import ApplicationContext

# project imports
from HTResearch.DataModel.enums import AccountType
from HTResearch.DataModel.globals import ORG_TYPE_CHOICES
from HTResearch.Utilities.context import DAOContext


class InviteForm(forms.Form):
    email = forms.EmailField(max_length=40)
    message = forms.CharField(widget=forms.Textarea, max_length=280, required=False)

    def clean_email(self):
        email = self.cleaned_data['email']
        ctx = ApplicationContext(DAOContext())
        dao = ctx.get_object('UserDAO')

        if dao.find(email=email):
            raise ValidationError('An account with that email already exists.')

        return email


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=40)
    password = forms.CharField(widget=forms.PasswordInput, min_length=8, max_length=40)


class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=25)
    last_name = forms.CharField(max_length=25)
    email = forms.EmailField(max_length=40)
    account_type = forms.ChoiceField(
        choices=((AccountType.COLLABORATOR, 'Collaborator'), (AccountType.CONTRIBUTOR, 'Contributor')))
    org_type = forms.ChoiceField(choices=ORG_TYPE_CHOICES, required=False)
    organization = forms.CharField(max_length=60, required=False)
    background = forms.CharField(widget=forms.Textarea, max_length=120)
    password = forms.CharField(widget=forms.PasswordInput, min_length=8, max_length=40)
    confirm_password = forms.CharField(widget=forms.PasswordInput, min_length=8, max_length=40)

    def clean_email(self):
        email = self.cleaned_data['email']
        ctx = ApplicationContext(DAOContext())
        dao = ctx.get_object('UserDAO')

        if dao.find(email=email):
            raise ValidationError('An account with that email already exists.')

        return email

    def clean_confirm_password(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']

        if password != confirm_password:
            raise ValidationError('Please ensure your passwords match.')

        return confirm_password