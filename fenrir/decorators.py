from django.contrib.auth import authenticate
from django.http import HttpResponse


def api_login(func):
    def wrap(request, *args, **kwargs):
        usr = request.POST.get('username')
        pwd = request.POST.get('password')
        request.user = authenticate(username=usr, password=pwd)

        if not request.user.is_authenticated():
            f_id = request.POST.get('facebook_id')
            request.user = authenticate(facebook_id=f_id)

        if not request.user.is_authenticated():
            return HttpResponse('User isn\'t authenticated!', status=401)

        return func(request, *args, **kwargs)

    wrap.__doc__ = func.__doc__
    wrap.__name__ = func.__name__
    return wrap


def api_call(func):
    def wrap(request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        request.user = authenticate(api_token=token)

        if not request.user.is_authenticated():
            return HttpResponse('User isn\'t authenticated!', status=401)

        return func(request, *args, **kwargs)

    wrap.__doc__ = func.__doc__
    wrap.__name__ = func.__name__
    return wrap
