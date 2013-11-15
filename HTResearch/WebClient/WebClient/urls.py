
from django.conf.urls import patterns, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

handler404 = 'HTResearch.WebClient.WebClient.views.get_http_404_page'
handler500 = handler404

urlpatterns = patterns('HTResearch.WebClient.WebClient.views',
    # Examples:
    # url(r'^$', 'HTResearch.WebClient.views.home', name='home'),
    # url(r'^HTResearch.WebClient/', include('HTResearch.WebClient.HTResearch.WebClient.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'index', name='index'),
    url(r'^search_organizations/$', 'search_organizations', name='search_organizations'),
    url(r'^search_contacts/$', 'search_contacts', name='search_contacts'),
    url(r'^organization/(\w+)', 'organization_profile', name='org_prof'),
    url(r'^contact/(\w+)', 'contact_profile', name='con_prof'),
    url(r'^coming_soon/$', 'unimplemented', name='unimplemented'),
)
