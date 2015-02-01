# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('volky', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='howl',
            name='updates',
            field=models.IntegerField(default=0, null=True),
            preserve_default=True,
        ),
    ]
