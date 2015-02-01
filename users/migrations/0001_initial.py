# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import users.storage


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Friendship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_blocked', models.BooleanField(default=False)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_favourite', models.BooleanField(default=False)),
                ('is_er', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now_add=True)),
                ('friend', models.ForeignKey(related_name='friendship_friend', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(related_name='friendship_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'friendships',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('device_token', models.CharField(max_length=255, unique=True, null=True, blank=True)),
                ('photo', models.ImageField(storage=users.storage.OverwriteStorage(), upload_to=b'')),
                ('locale', models.CharField(default=b'English', max_length=32)),
                ('is_using_facebook', models.BooleanField(default=False)),
                ('facebook_id', models.CharField(max_length=32, unique=True, null=True, blank=True)),
                ('updated_on', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'profiles',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='friendship',
            unique_together=set([('user', 'friend')]),
        ),
    ]
