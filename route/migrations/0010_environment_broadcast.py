# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-13 07:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0009_auto_20170813_1441'),
    ]

    operations = [
        migrations.AddField(
            model_name='environment',
            name='broadcast',
            field=models.CharField(default=0, max_length=20, verbose_name='广播地址'),
            preserve_default=False,
        ),
    ]
