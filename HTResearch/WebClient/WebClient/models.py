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


class RequestOrgForm(forms.Form):
    url = forms.URLField()

    def clean_url(self):
        url = self.cleaned_data['url']
        ctx = ApplicationContext(DAOContext())
        dao = ctx.get_object('OrganizationDAO')

        if dao.find(organization_url=url):
            raise ValidationError("Oops! Looks like we already have information on that organization.")

        return url


class EditContactForm(forms.Form):
    contact_id = forms.CharField(widget=forms.HiddenInput)
    first_name = forms.CharField(max_length=25, required=False)
    last_name = forms.CharField(max_length=25, required=False)
    phone = forms.CharField(required=False)
    email = forms.EmailField(max_length=40, required=False)
    position = forms.CharField(max_length=60, required=False)
    invalid = forms.BooleanField()

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        try:
            stripped_phone = phone.translate(None, '()-. ')
            return stripped_phone
        except:
            raise ValidationError("Please enter a valid phone number.")

    def clean_email(self):
        email = self.cleaned_data['email']
        ctx = ApplicationContext(DAOContext())
        contact_dao = ctx.get_object('ContactDAO')
        user_dao = ctx.get_object('UserDAO')

        if contact_dao.find(email=email) or user_dao.find(email=email):
            raise ValidationError("A contact with that email address already exists.")


class EditContactModel():
    def __init__(self, contact=None, form=None):
        if contact:
            self.contact_id = str(contact.id)
            self.first_name = contact.first_name if contact.first_name else ""
            self.last_name = contact.last_name if contact.last_name else ""
            self.email = contact.email if contact.email else ""
            self.phone = str(contact.phone) if contact.phone else ""
            self.position = contact.position if contact.position else ""
            self.invalid = not contact.valid
        elif form:
            self.contact_id = form['contact_id'] if form['contact_id'] else ""
            self.first_name = form['first_name'] if form['first_name'] else ""
            self.last_name = form['last_name'] if form['last_name'] else ""
            self.email = form['email'] if form['email'] else ""
            self.phone = form['phone'] if form['phone'] else ""
            self.position = form['position'] if form['position'] else ""
            self.invalid = form['invalid'] if form['invalid'] else ""