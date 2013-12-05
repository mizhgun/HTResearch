from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=80)
    password = forms.CharField(min_length=8, max_length=80)