from django.conf.urls import patterns, url

handler403 = 'HTResearch.WebClient.WebClient.views.unauthorized'
handler404 = 'HTResearch.WebClient.WebClient.views.shared_views.get_http_404_page'
handler500 = 'HTResearch.WebClient.WebClient.views.shared_views.get_http_500_page'


urlpatterns = patterns('HTResearch.WebClient.WebClient.views.api_views',
                       url(r'^api/heatmap-coordinates/$', 'heatmap_coordinates', name='heatmap-coordinates'),
                       url(r'^api/search-organizations/$', 'search_organizations', name='search-organizations'),
                       url(r'^api/search-contacts/$', 'search_contacts', name='search-contacts'),
                       url(r'^api/search-publications/$', 'search_publications', name='search-publications'),
                       url(r'^api/get-org-rank-rows/$', 'get_org_rank_rows', name='get-org-rank-rows'),
                       url(r'^api/get-org-keywords/$', 'get_org_keywords', name='get-org-keywords'),
                       url(r'^api/partner-map/$', 'org_partner_map', name='org-partner-map'),
                       url(r'^api/orgs-by-region/$', 'orgs_by_region', name='orgs-by-region'),
                       url(r'^api/orgs-by-type/$', 'orgs_by_type', name='orgs-by-type'),
                       url(r'^api/orgs-by-members/$', 'orgs_by_members', name='orgs-by-members'),
                       url(r'^api/org-count/$', 'org_count', name='org-count'),
                       url(r'^api/contact-count/$', 'contact_count', name='contact-count'),
                       url(r'^api/pub-count/$', 'pub_count', name='pub-count'),)

urlpatterns += patterns('HTResearch.WebClient.WebClient.views.shared_views',
                        url(r'^$', 'index', name='index'),
                        url(r'^welcome/$', 'welcome', name='welcome'),
                        url(r'^get-started/$', 'get_started', name='get-started'),
                        url(r'^about/$', 'about', name='about'),
                        url(r'^dashboard/$', 'dashboard', name='dashboard'),)

urlpatterns += patterns('HTResearch.WebClient.WebClient.views.org_views',
                        url(r'^organization/(\w+)', 'organization_profile', name='org-prof'),
                        url(r'^org-rank/$', 'org_rank', name='org-rank'),
                        url(r'^request-organization/$', 'request_organization', name='request-organization'),
                        url(r'^edit-organization/(\w+)', 'edit_organization', name='edit-organization'),)

urlpatterns += patterns('HTResearch.WebClient.WebClient.views.contact_views',
                        url(r'^contact/(\w+)', 'contact_profile', name='con-prof'),
                        url(r'^edit-contact/(\w+)', 'edit_contact', name='edit-contact'),
                        )

urlpatterns += patterns('HTResearch.WebClient.WebClient.views.user_views',
                        url(r'^login/$', 'login', name='login'),
                        url(r'^logout/$', 'logout', name='logout'),
                        url(r'^signup/$', 'signup', name='signup'),
                        url(r'^invite/$', 'send_invite', name='invite'),
                        url(r'^account-settings/$', 'manage_account', name='manage'),)
