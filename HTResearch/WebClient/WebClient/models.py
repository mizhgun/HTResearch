from django import forms

from HTResearch.DataModel.enums import AccountType, AffiliationType


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=80)
    password = forms.CharField(min_length=8, max_length=80)


class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=25)
    last_name = forms.CharField(max_length=25)
    email = forms.EmailField(max_length=60, required=True)
    account_type = forms.ChoiceField(choices=((AccountType.BASIC, 'Basic'), (AccountType.CONTRIBUTOR, 'Contributor')))
    affiliation = forms.ChoiceField(
        choices=((AffiliationType.STUDENT, 'Student'), (AffiliationType.EMPLOYEE, 'Employee')), required=False)
    organization = forms.CharField(max_length=60, required=False)
    background = forms.CharField(widget=forms.Textarea, max_length=120)
    password = forms.CharField(widget=forms.PasswordInput, max_length=80)
    confirm_password = forms.CharField(widget=forms.PasswordInput, max_length=80)