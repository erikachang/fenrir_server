from django.http import HttpResponse, HttpResponseNotFound
from django.http import HttpResponseBadRequest
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST

from fenrir.decorators import api_call
from volky.decorators import app_view
from users.models import Friendship
from volky.models import Howl
from volky.apns_queue import APNSQueueSystem
from aps import Aps

q_system = APNSQueueSystem()


# Create your views here.
@app_view
@api_call
@require_POST
def howl(request):
    try:
        receiver = request.POST['receiver']
        description = request.POST['description']
        latitude = request.POST['latitude']
        longitude = request.POST['longitude']
    except KeyError:
        return HttpResponseBadRequest()

    user = request.user

    try:
        friend = User.objects.get(username=receiver)
    except User.DoesNotExist:
        return HttpResponseNotFound()

    friendship, created = Friendship.objects.get_or_create(
        user=friend,
        friend=user
    )

    if not created:
        if friendship.is_blocked:
            return HttpResponse(status=204)
        elif friendship.is_deleted:
            friendship.is_deleted = False
            friendship.save()

    howl, created = Howl.objects.update_or_create(
        friendship=friendship,
        defaults={
            'latitude': latitude,
            'longitude': longitude,
            'description': description
        }
    )

    if friend.profile.device_token is None:
        return HttpResponse(status=204)

    aps = Aps(user.username, description, latitude, longitude)
    q_system.enqueue_aps(friend.profile.device_token, aps.dict())

    return HttpResponse(status=204)


@app_view
@api_call
@require_POST
def broadcast_howl(request):
    try:
        description = request.POST['description']
        latitude = request.POST['latitude']
        longitude = request.POST['longitude']
    except KeyError:
        return HttpResponseBadRequest()

    user = request.user

    tokens = []

    friendships = Friendship.objects.filter(
        user=user,
        is_deleted=False,
        is_favourite=True
    )

    for friendship in friendships:
        r_friendship, created = Friendship.objects.get_or_create(
            user=friendship.friend,
            friend=user
        )

        if not created:
            if r_friendship.is_blocked:
                return HttpResponse(status=204)
            elif r_friendship.is_deleted:
                r_friendship.is_deleted = False
                r_friendship.save()

        howl, created = Howl.objects.update_or_create(
            friendship=r_friendship,
            defaults={
                'latitude': latitude,
                'longitude': longitude,
                'description': description
            }
        )

        if friendship.friend.profile.device_token is not None:
            tokens.append(friendship.friend.profile.device_token)

    aps = Aps(user.username, description, latitude, longitude)
    q_system.enqueue_multiple(tokens, aps.dict())

    return HttpResponse(status=204)


@app_view
@api_call
@require_POST
def distress_howl(request):
    try:
        description = request.POST['description']
        latitude = request.POST['latitude']
        longitude = request.POST['longitude']
    except KeyError:
        return HttpResponseBadRequest()

    user = request.user

    tokens = []

    friendships = Friendship.objects.filter(
        user=user,
        is_deleted=False,
        is_er=True
    )

    for friendship in friendships:
        r_friendship, created = Friendship.objects.get_or_create(
            user=friendship.friend,
            friend=user
        )

        if not created:
            if r_friendship.is_blocked:
                return HttpResponse(status=204)
            elif r_friendship.is_deleted:
                r_friendship.is_deleted = False
                r_friendship.save()

        howl, created = Howl.objects.update_or_create(
            friendship=r_friendship,
            defaults={
                'latitude': latitude,
                'longitude': longitude,
                'description': "S.O.S.: %s" % (description)
                }
        )

        if friendship.friend.profile.device_token is not None:
            tokens.append(friendship.friend.profile.device_token)

    aps = Aps(user.username, description, latitude, longitude,
        sound='er.wav', h_type='ER')
    q_system.enqueue_multiple(tokens, aps.dict())

    return HttpResponse(status=204)
