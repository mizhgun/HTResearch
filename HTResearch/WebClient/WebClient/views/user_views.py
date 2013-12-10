from django.shortcuts import render_to_response


def login(request):
    return render_to_response('login.html')


def signup(request):
    return render_to_response('signup.html')