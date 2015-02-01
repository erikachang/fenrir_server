from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.http import HttpResponseNotFound, HttpResponseBadRequest
from django.views.generic import View
from django.contrib.auth.models import User
from django.conf import settings

from models import Friendship

from fenrir.decorators import api_call
from volky.decorators import app_view


class VolkyUser(View):
    def get(self, request, username):
        if request.user.username != username:
            return HttpResponseForbidden()

        return JsonResponse(request.user.profile.info())

    def post(self, request, username):
        if request.user.username != username:
            return HttpResponseForbidden()

        if 'profile_photo' in request.FILES:
            request.user.profile.photo = request.FILES.get('profile_photo')
            request.user.profile.save()
            return HttpResponse(status=200, content='Profile photo updated successfully.')
        elif 'device_token' in request.POST:
            request.user.profile.change_device(request.POST.get('device_token'))
            return HttpResponse(status=200, content='Device Token updated successfully.')
        elif 'first_name' in request.POST:
            request.user.first_name = request.POST.get('first_name')
            if 'last_name' in request.POST:
                request.user.last_name = request.POST.get('last_name')
            request.user.save()
            return HttpResponse(status=200)

        return HttpResponse(status=204)


class VolkyFriends(View):
    def get(self, request, username):
        user = request.user

        if user.username != username:
            return HttpResponseForbidden()

        key = 'friendships'
        friends_dictionary = {key: []}

        friendships = Friendship.objects.filter(user=user, is_deleted=False)
        for friendship in friendships:
            friends_dictionary[key].append(friendship.info())

        if len(friends_dictionary.get(key)) == 0:
            return HttpResponse(status=204)

        return JsonResponse(friends_dictionary)

    def post(self, request, username):
        try:
            friendname = request.POST['friendname']
        except KeyError:
            return HttpResponseBadRequest()

        user = request.user

        if user.username != username:
            return HttpResponseForbidden()

        friend = User.objects.filter(username=friendname).first()
        if friend is None:
            return HttpResponseNotFound()

        friendship, created = Friendship.objects.get_or_create(
            user=user,
            friend=friend
        )

        if not created and friendship.is_deleted:
            friendship.is_deleted = False
            friendship.save()

        response = JsonResponse(friendship.info())
        response.status_code = 201
        return response


class VolkyFriend(View):
    def get(self, request, username, friendname):
        user = request.user

        if user.username != username:
            return HttpResponseForbidden()

        friend = User.objects.get(username=friendname)
        friendship = Friendship.objects.get(user=user, friend=friend)

        return JsonResponse(friendship.info())

    def post(self, request, username, friendname):
        user = request.user

        if user.username != username:
            return HttpResponseForbidden()

        friend = User.objects.get(username=friendname)
        friendship = Friendship.objects.get(user=user, friend=friend)

        if 'is_blocked' in request.POST:
            friendship.is_blocked = request.POST.get('is_blocked') == '1'
        if 'is_favourite' in request.POST:
            friendship.is_favourite = request.POST.get('is_favourite') == '1'
        if 'is_er' in request.POST:
            friendship.is_er = request.POST.get('is_er') == '1'

        friendship.save()

        return HttpResponse(status=204)

    def delete(self, request, username, friendname):
        user = request.user

        if user.username != username:
            return HttpResponseForbidden()

        friend = User.objects.get(username=friendname)
        friendship = Friendship.objects.get(user=user, friend=friend)

        friendship.is_deleted = True
        friendship.save()
        return HttpResponse(status=204)


@app_view
@api_call
def user_photos(request, fn):
    response = HttpResponse(content_type='image/jpeg')
    response['X-Accel-Redirect'] = '%s/%s' % (settings.MEDIA_URL, fn)
    return response
