# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-26 15:28
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='service',
            unique_together=set([('service_id', 'scene_id', 'dfa')]),
        ),
    ]