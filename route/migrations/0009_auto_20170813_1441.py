# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-13 06:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0008_auto_20170806_1023'),
    ]

    operations = [
        migrations.RenameField(
            model_name='serviceenv',
            old_name='operate_type',
            new_name='zk_type',
        ),
        migrations.AddField(
            model_name='serviceenv',
            name='giraffe_type',
            field=models.NullBooleanField(),
        ),
    ]