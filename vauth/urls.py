from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^signup/$', 'vauth.views.sign_up'),
    url(r'^login/$', 'vauth.views.auth_login'),
    url(r'^logout/$', 'vauth.views.auth_logout'),
    url(r'^change_password/$', 'vauth.views.change_password'),
    url(r'^forgot/$', 'vauth.views.forgot_password')
)
