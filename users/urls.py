from django.conf.urls import patterns, url

from users.views import VolkyUser, VolkyFriends, VolkyFriend
from fenrir.decorators import api_call
from volky.decorators import app_view

urlpatterns = patterns(
    '',
    url(r'^(?P<username>[a-z][0-9a-z]+)$',
        app_view(api_call(VolkyUser.as_view()))),
    url(r'^(?P<username>[a-z][0-9a-z]+)/friends/$',
        app_view(api_call(VolkyFriends.as_view()))),
    url(r'^(?P<username>[a-z][0-9a-z]+)/friends/(?P<friendname>[a-z][0-9a-z]+)$',
        app_view(api_call(VolkyFriend.as_view()))),
)
