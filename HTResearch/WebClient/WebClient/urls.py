from django.conf.urls import patterns, include, url
from HTResearch.WebClient.webclient.views import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'htresearch.WebClient.views.home', name='home'),
    # url(r'^htresearch.WebClient/', include('htresearch.WebClient.htresearch.WebClient.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', index, name='index'),
    url(r'^organization/', organization_profile, name='org_prof')
)
