# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vauth', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apitoken',
            name='issued_on',
            field=models.DateTimeField(auto_now_add=True, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='apitoken',
            name='token',
            field=models.CharField(max_length=128, unique=True, null=True),
            preserve_default=True,
        ),
    ]
