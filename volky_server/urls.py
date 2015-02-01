from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
admin.autodiscover()
import settings

urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'miceware_ping.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'fenrir.views.status'),
    url(r'^auth/', include('vauth.urls')),
    url(r'^users/', include('users.urls')),
    url(r'^volky/', include('volky.urls')),
    url(r'^photos/(?P<fn>.*)$', 'users.views.user_photos'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
