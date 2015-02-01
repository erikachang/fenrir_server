from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^howl/$', 'volky.views.howl'),
    url(r'^broadcast/$', 'volky.views.broadcast_howl'),
    url(r'^distress/$', 'volky.views.distress_howl'),
)
