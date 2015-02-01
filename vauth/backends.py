from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User, AnonymousUser
from vauth.models import ApiToken
from users.models import Profile


class BasicAuthentication(object):
    def authenticate(self, username=None, password=None):
        if username is not None and password is not None:
            try:
                user = User.objects.select_related().get(username=username)
                if user.has_usable_password():
                    if check_password(password, user.password):
                        return user
            except User.DoesNotExist:
                pass
        return AnonymousUser()

    def get_user(self, user_id):
        try:
            return User.objects.select_related().get(pk=user_id)
        except User.DoesNotExist:
            return AnonymousUser()


class ApiTokenAuthentication(object):
    def authenticate(self, api_token=None):
        if api_token is not None and api_token != '':
            try:
                apitoken = ApiToken.objects.get(token=api_token)
                # user = User.objects.select_related().get(user=apitoken.user)
                return apitoken.user
            except ApiToken.DoesNotExist:
                pass
        return AnonymousUser()

    def get_user(self, user_id):
        try:
            return User.objects.select_related().get(pk=user_id)
        except User.DoesNotExist:
            return AnonymousUser()


class FacebookAuthentication(object):
    def authenticate(self, facebook_id=None):
        if facebook_id is not None and facebook_id != '':
            try:
                profile = Profile.objects.get(facebook_id=facebook_id)
                return profile.user
            except Profile.DoesNotExist:
                pass
        return AnonymousUser()

    def get_user(self, user_id):
        try:
            return User.objects.select_related().get(pk=user_id)
        except User.DoesNotExist:
            return AnonymousUser()
