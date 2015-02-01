from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.http import HttpResponseNotFound, HttpResponseBadRequest
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User

from vauth.models import ApiToken
from users.models import Profile
from fenrir.decorators import api_login, api_call
from volky.decorators import app_view


@app_view
@require_POST
def sign_up(request):
    # Fields inside try-except are mandatory.
    try:
        username = request.POST['username']
        email = request.POST['email']
        profile_photo = request.FILES['profile_photo']
        # Password and Facebook ID are mutually exclusive.
        facebook_id = request.POST.get('facebook_id')
        if facebook_id is None:
            password = request.POST['password']
    except KeyError:
        return HttpResponseBadRequest()

    if User.objects.filter(username=username).exists():
        return HttpResponse(status=409, content='username')
    if User.objects.filter(email=email).exists():
        return HttpResponse(status=409, content='email')

    if facebook_id is not None and facebook_id != '':
        if Profile.objects.filter(facebook_id=facebook_id).exists():
            return HttpResponse(status=409, content='facebook account')
        user = User.objects.create_user(username, email)
        Profile.objects.create(user=user,
                               photo=profile_photo,
                               facebook_id=facebook_id,
                               is_using_facebook=True)
    else:
        user = User.objects.create_user(username, email, password)
        Profile.objects.create(user=user, photo=profile_photo)

    ApiToken.objects.create(user=user)
    return HttpResponse(status=204)


@app_view
@require_POST
def link_facebook(request):
    try:
        username = request.POST['username']
        password = request.POST['password']
        facebook_id = request.POST['facebook_id']
    except KeyError:
        return HttpResponseBadRequest()
    user = User.objects.select_related().get(username=username).first()
    if check_password(password, user.password):
        user.set_facebook_identity(facebook_id)
    else:
        return HttpResponse(status=401)
    return HttpResponse(status=200)


@app_view
@api_login
@require_POST
def auth_login(request):
    """ Reads device token from POST dictionary and saves it to the
    authenticated user's profile. If there are any existing profiles using
    the given token, removes it. After doing so, generates a new ApiToken and
    assigns it to the authenticated user.
    """
    device = request.POST.get('device_token')
    if device is not None:
        request.user.profile.change_device(device)
    if not hasattr(request.user, 'apitoken'):
        ApiToken.objects.create(user=request.user)
    request.user.apitoken.gen_token()
    return JsonResponse(request.user.apitoken.info())


@app_view
@api_call
@require_POST
def auth_logout(request):
    """ Cleans ApiToken information related to the authenticated user. Also
    cleans the device token registered on the user's profile.
    """
    request.user.apitoken.clean()
    request.user.profile.clean()
    return HttpResponse(status=204)


@app_view
@api_call
@require_POST
def change_password(request):
    try:
        new_pwd = request.POST['new_pwd']
        curr_pwd = request.POST['password']
    except KeyError:
        return HttpResponseBadRequest()

    if not check_password(curr_pwd, request.user.password):
        return HttpResponse(status=401)

    request.user.set_password(new_pwd)
    request.user.save()
    return HttpResponse(status=204)


@app_view
@require_POST
def forgot_password(request):
    try:
        email = request.POST['email']
    except KeyError:
        return HttpResponseBadRequest()

    user = User.objects.select_related().filter(email=email).first()

    if user is None:
        return HttpResponseNotFound()

    if user.profile.is_using_facebook:
        return HttpResponseForbidden()

    r = user.reset_password()

    return HttpResponse(r.status_code, status=r.status_code)
