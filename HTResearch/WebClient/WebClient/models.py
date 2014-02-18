# stdlib imports
from django import forms
from django.core.exceptions import ValidationError
from springpython.context import ApplicationContext

# project imports
from HTResearch.DataModel.enums import AccountType
from HTResearch.DataModel.globals import ORG_TYPE_CHOICES
from HTResearch.Utilities.context import DAOContext
from HTResearch.Utilities.url_tools import UrlUtility


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

        try:
            url = UrlUtility().get_domain(url)
        except:
            raise ValidationError("Oops! We couldn't find information on that domain.")

        if dao.find(organization_url=url):
            raise ValidationError("Oops! Looks like we already have information on that organization.")

        return url


class EditOrganizationForm(forms.Form):
    name = forms.CharField(max_length=80, required=False)
    address = forms.CharField(required=False)
    organization_url = forms.URLField(required=False)
    facebook = forms.URLField(required=False, max_length=60)
    twitter = forms.URLField(required=False, max_length=60)
    invalid = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        emails = kwargs.pop('emails') if 'emails' in kwargs else []
        phone_numbers = kwargs.pop('phone_numbers') if 'phone_numbers' in kwargs else []
        types = kwargs.pop('types') if 'types' in kwargs else []

        super(EditOrganizationForm, self).__init__(*args, **kwargs)
        i = 1
        for email in emails:
            self.fields["email_{0}".format(i)] = forms.EmailField(required=False,
                                                                  initial=email,
                                                                  label="Email {0}".format(i))

        i = 1
        for num in phone_numbers:
            self.fields["phone_{0}".format(i)] = forms.CharField(required=False,
                                                                 initial=num,
                                                                 label="Phone {0}".format(i))

        i = 1
        for org_type in types:
            self.fields["type_{0}".format(i)] = forms.ChoiceField(required=False,
                                                                  choices=ORG_TYPE_CHOICES,
                                                                  initial=org_type,
                                                                  label="Type {0}".format(i))

    def clean_organization_url(self):
        url = self.cleaned_data['organization_url']
        if url:
            try:
                return UrlUtility.get_domain(url)
            except:
                raise ValidationError("Oops! We couldn't recognize that URL's domain.")
        else:
            return None

    def emails(self):
        return self._get_dynamic_attrs('email')

    def phone_numbers(self):
        return self._get_dynamic_attrs('phone')

    def types(self):
        return self._get_dynamic_attrs('type')

    def _get_dynamic_attrs(self, key):
        if hasattr(self, 'cleaned_data'):
            for name, value in self.cleaned_data.items():
                if name.startswith(key):
                    field = self.fields[name]
                    yield {'id': 'id_' + name,
                           'label': field.label,
                           'name': name,
                           'value': value}
        else:
            for name, field in self.fields.items():
                if name.startswith(key):
                    yield {'id': 'id_' + name,
                           'label': field.label,
                           'name': name,
                           'value': field.initial}


class EditContactForm(forms.Form):
    first_name = forms.CharField(max_length=25, required=False)
    last_name = forms.CharField(max_length=25, required=False)
    email = forms.EmailField(max_length=40, required=False)
    position = forms.CharField(max_length=60, required=False)
    invalid = forms.BooleanField(required=False)

    def clean_phone(self):
        phone = str(self.cleaned_data['phone'])
        try:
            stripped_phone = phone.translate(None, '()-. ')
            return stripped_phone
        except:
            raise ValidationError("Please enter a valid phone number.")

    def __init__(self, *args, **kwargs):
        phones = kwargs.pop('phones') if 'phones' in kwargs else []

        super(EditContactForm, self).__init__(*args, **kwargs)
        i = 1
        for num in phones:
            self.fields["phone_{0}".format(i)] = forms.CharField(required=False,
                                                                 initial=num,
                                                                 label="Phone {0}".format(i))

    def phones(self):
        return self._get_dynamic_attrs('phone')

    def _get_dynamic_attrs(self, key):
        if hasattr(self, 'cleaned_data'):
            for clean_key, value in self.cleaned_data.items():
                if clean_key.startswith(key):
                    field = self.fields[clean_key]
                    yield {'id': 'id_' + clean_key,
                           'label': field.label,
                           'name': clean_key,
                           'value': value}
        else:
            for name, field in self.fields.items():
                if name.startswith(key):
                    yield {'id': 'id_' + name,
                           'label': field.label,
                           'name': name,
                           'value': field.initial}
