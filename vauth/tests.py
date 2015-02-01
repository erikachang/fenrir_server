from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from vauth import views
from django.http import HttpRequest
# Create your tests here.

TEST_USER = 'test_user'
TEST_PWD = 'test_password'


def sign_up():
    request = HttpRequest()
    request.method = 'POST'
    request.META['HTTP_USER_AGENT'] = 'Volky'
    request.POST['username'] = TEST_USER
    request.POST['password'] = TEST_PWD
    request.POST['email'] = 'test@test.test'
    request.FILES['profile_photo'] = '%stest_avatar.jpg' % settings.MEDIA_ROOT
    return views.sign_up(request)


def login():
    request = HttpRequest()
    request.method = 'POST'
    request.META['HTTP_USER_AGENT'] = 'Volky'
    request.POST['username'] = TEST_USER
    request.POST['password'] = TEST_PWD
    request.POST['device_token'] = 'test_token'
    request.user = User.objects.get(username=TEST_USER)
    return views.auth_login(request)


def logout():
    request = HttpRequest()
    request.META['HTTP_USER_AGENT'] = 'Volky'
    request.method = 'POST'
    request.user = User.objects.get(username=TEST_USER)
    request.META['HTTP_AUTHORIZATION'] = request.user.apitoken.token
    return views.auth_logout(request)


class SignUpTestCase(TestCase):
    def test_signup(self):
        response = sign_up()
        self.assertEqual(response.status_code, 204)

        user = User.objects.filter(username=TEST_USER).first()
        self.assertIsNotNone(user)
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsNotNone(user.profile.photo)
        self.assertTrue(hasattr(user, 'apitoken'))


class LoginTestCase(TestCase):
    def setUp(self):
        sign_up()

    def test_login(self):
        response = login()
        self.assertEqual(response.status_code, 200)

        user = User.objects.filter(username=TEST_USER).first()
        self.assertIsNotNone(user)
        self.assertTrue(hasattr(user, 'apitoken'))
        self.assertIsNotNone(user.apitoken.token)
        self.assertIsNotNone(user.profile.device_token)


class LogoutTestCase(TestCase):
    def setUp(self):
        sign_up()
        self.apitoken = login()

    def test_logout(self):
        response = logout()
        self.assertEqual(response.status_code, 204)

        user = User.objects.filter(username=TEST_USER).first()
        self.assertIsNotNone(user)
        self.assertIsNone(user.apitoken.token)
        self.assertIsNone(user.profile.device_token)
