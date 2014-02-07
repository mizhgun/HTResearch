from django.conf.urls import patterns, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

handler404 = 'HTResearch.WebClient.WebClient.views.get_http_404_page'
handler500 = handler404

urlpatterns = patterns('HTResearch.WebClient.WebClient.views.shared_views',
                       # Examples:
                       # url(r'^$', 'HTResearch.WebClient.views.home', name='home'),
                       # url(r'^HTResearch.WebClient/', include('HTResearch.WebClient.HTResearch.WebClient.urls')),

                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       # url(r'^admin/', include(admin.site.urls)),

                       url(r'^$', 'index', name='index'),
                       url(r'^heatmap-coordinates/$', 'heatmap_coordinates', name='heatmap-coordinates'),
                       url(r'^coming-soon/$', 'unimplemented', name='unimplemented'),
                       url(r'^welcome/$', 'welcome', name='welcome'),
                       url(r'^get-started/$', 'get_started', name='get-started'),
)

urlpatterns += patterns('HTResearch.WebClient.WebClient.views.org_views',
                        url(r'^search-organizations/$', 'search_organizations', name='search-organizations'),
                        url(r'^organization/(\w+)', 'organization_profile', name='org-prof'),
                        url(r'^org-rank$', 'org_rank', name='org-rank'),
                        url(r'^org-rank/(\w+)$', 'org_rank', name='org-rank'),
                        url(r'^get-org-rank-rows/$', 'get_org_rank_rows', name='get-org-rank-rows'),
                        url(r'^get-org-keywords/$', 'get_org_keywords', name='get-org-keywords'),
                        url(r'^request-organization/$', 'request_organization', name='request_organization'),
)

urlpatterns += patterns('HTResearch.WebClient.WebClient.views.contact_views',
                        url(r'^search-contacts/$', 'search_contacts', name='search-contacts'),
                        url(r'^contact/(\w+)', 'contact_profile', name='con-prof'),
                        url(r'^edit-contact/(\w+)', 'edit_contact', name='edit-contact'),
)

urlpatterns += patterns('HTResearch.WebClient.WebClient.views.publication_views',
                        url(r'^search-publications/$', 'search_publications', name='search-publications'),
)

urlpatterns += patterns('HTResearch.WebClient.WebClient.views.user_views',
                        url(r'^login/$', 'login', name='login'),
                        url(r'^logout/$', 'logout', name='logout'),
                        url(r'^signup/$', 'signup', name='signup'),
                        url(r'^invite/$', 'send_invite', name='invite'),
)
