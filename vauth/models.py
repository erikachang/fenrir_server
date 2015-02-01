from django.db import models
from django.contrib.auth.models import User
from django.template.loader import get_template
from django.template import Context
from django.conf import settings
from datetime import datetime

import binascii
import hashlib
import os

import requests


class ApiToken(models.Model):
    user = models.OneToOneField(User)
    token = models.CharField(max_length=128, unique=True, null=True)
    issued_on = models.DateTimeField(auto_now_add=True, null=True)

    def info(self):
        data = {
            'apitoken': {
                'username': self.user.username,
                'token': self.token,
                'issued_on': self.issued_on,
            }
        }
        return data

    def clean(self, *args, **kwargs):
        self.token = None
        self.issued_on = None
        super(ApiToken, self).save(*args, **kwargs)

    def gen_token(self):
        time = datetime.now()
        token_base = hashlib.sha224(
            self.user.username + str(time) +
            binascii.hexlify(os.urandom(64))).hexdigest()

        self.token = hashlib.sha224(token_base).hexdigest()
        self.issued_on = time
        self.save()

    class Meta:
        db_table = 'apitokens'


def reset_password(self):
    password = User.objects.make_random_password(length=8)
    self.set_password(password)
    self.save()

    _text = get_template('forgot_password.txt')
    _html = get_template('forgot_password.html')
    _c = Context({'username': self.username, 'password': password})

    data = {
        "from": 'team@miceware.co',
        "to": [self.email],
        "subject": 'Your password has been reset!',
        "text": _text.render(_c),
        "html": _html.render(_c)
    }

    return requests.post(
        settings.MAILGUN_ENDPOINT,
        auth=("api", settings.MAILGUN_APITOKEN),
        data=data
        )


def set_facebook_identity(self, facebook_id):
    self.profile.facebook_id = facebook_id
    self.profile.is_using_facebook = True
    self.set_unusable_password()


User.add_to_class('reset_password', reset_password)
User.add_to_class('set_facebook_identity', set_facebook_identity)
