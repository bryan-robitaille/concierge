# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-11-21 17:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmailDomainGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='EmailRegExValidator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('regex', models.CharField(max_length=100, verbose_name='Regex/domain')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='emailvalidator.EmailDomainGroup')),
            ],
        ),
        migrations.RunSQL(
          [('INSERT INTO emailvalidator_emaildomaingroup (name) values (%s)', ['Any'])],
        ),
        migrations.RunSQL(
          [('INSERT INTO emailvalidator_emailregexvalidator (regex, group_id) values (%s, 1)', ['.*'])]
        ),
    ]
