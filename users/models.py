from django.db import models
from storage import OverwriteStorage
from django.contrib.auth.models import User
from datetime import datetime

fs = OverwriteStorage()


class Profile(models.Model):
    user = models.OneToOneField(User)
    device_token = models.CharField(max_length=255,
                                    unique=True,
                                    blank=True,
                                    null=True)
    photo = models.ImageField(storage=fs)
    locale = models.CharField(max_length=32, default='English')
    is_using_facebook = models.BooleanField(default=False)
    facebook_id = models.CharField(max_length=32,
                                   null=True,
                                   blank=True,
                                   unique=True)
    updated_on = models.DateTimeField(auto_now_add=True)

    def info(self):
        data = {
            'profile': {
                'screenname': '%s %s' %
                              (self.user.first_name, self.user.last_name),
                'username': self.user.username,
                'email': self.user.email,
                'photo': self.photo.name,
                'updated_on': self.updated_on,
            }
        }
        return data

    def save(self, *args, **kwargs):
        self.updated_on = datetime.now()
        super(Profile, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        self.device_token = None
        self.save()

    def change_device(self, device):
        profile = Profile.objects.filter(device_token=device).first()
        if profile is not None:
            profile.device_token = None
            profile.save()
        self.device_token = device
        self.save()

    class Meta:
        db_table = 'profiles'


class Friendship(models.Model):
    user = models.ForeignKey(User, related_name='friendship_user')
    friend = models.ForeignKey(User, related_name='friendship_friend')
    is_blocked = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_favourite = models.BooleanField(default=False)
    is_er = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)

    def info(self):
        howl = {}
        if hasattr(self, 'howl'):
            howl = self.howl.info()
        data = {
            'friendship': {
                'user': self.user.username,
                'friend': {
                    'username': self.friend.username,
                    'updated_on': self.friend.profile.updated_on,
                    'email': self.user.email,
                    'photo': self.friend.profile.photo.name,
                },
                'is_blocked': self.is_blocked,
                'is_deleted': self.is_deleted,
                'is_favourite': self.is_favourite,
                'is_er': self.is_er,
                'updated_on': self.updated_on,
                'howl': howl.get('howl'),
            },
        }
        return data

    def save(self, *args, **kwargs):
        self.updated_on = datetime.now()
        super(Friendship, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('user', 'friend')
        db_table = 'friendships'
