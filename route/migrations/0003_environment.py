# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-30 08:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0002_auto_20170726_2328'),
    ]

    operations = [
        migrations.CreateModel(
            name='Environment',
            fields=[
                ('name', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('desc', models.CharField(max_length=50)),
                ('zk_idc1', models.CharField(max_length=50)),
                ('zk_idc2', models.CharField(max_length=50)),
                ('namesrv', models.CharField(max_length=50)),
                ('broker_idc1', models.CharField(max_length=50)),
                ('broker_idc2', models.CharField(max_length=50)),
                ('cluster_name_idc1', models.CharField(max_length=50)),
                ('cluster_name_idc2', models.CharField(max_length=50)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='route.Service')),
            ],
        ),
    ]
