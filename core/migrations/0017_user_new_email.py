# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-18 09:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_eventlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='new_email',
            field=models.EmailField(default=None, max_length=255, null=True),
        ),
    ]
