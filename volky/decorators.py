from django.http import HttpResponseNotFound
from django.conf import settings


class WandererResponse(HttpResponseNotFound):
    def __init__(self, path):
        content = '<h1>Not Found</h1>' \
                  '<p>The requested URL %s was not found on this server.</p>' % \
                  (path)
        super(WandererResponse, self).__init__(content)


def app_view(func):
    def wrap(request, *args, **kwargs):
        if not settings.DEBUG:
            source = request.META.get('HTTP_USER_AGENT')

            if source is None or 'Volky' not in source:
                return WandererResponse(request.path)

        return func(request, *args, **kwargs)

    wrap.__doc__ = func.__doc__
    wrap.__name__ = func.__name__
    return wrap
