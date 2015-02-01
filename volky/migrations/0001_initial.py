# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Howl',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('latitude', models.DecimalField(max_digits=8, decimal_places=6)),
                ('longitude', models.DecimalField(max_digits=9, decimal_places=6)),
                ('description', models.CharField(max_length=60)),
                ('updated_on', models.DateTimeField()),
                ('friendship', models.OneToOneField(to='users.Friendship')),
            ],
            options={
                'db_table': 'howls',
            },
            bases=(models.Model,),
        ),
    ]
