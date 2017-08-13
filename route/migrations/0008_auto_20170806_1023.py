# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-06 02:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0007_auto_20170731_2117'),
    ]

    operations = [
        migrations.AddField(
            model_name='environment',
            name='idc1_code',
            field=models.CharField(default=django.utils.timezone.now, max_length=10, verbose_name='idc1的编号'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='environment',
            name='idc2_code',
            field=models.CharField(default='j', max_length=10, verbose_name='idc2的编号'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='environment',
            name='orgId',
            field=models.CharField(default='8888', max_length=10, verbose_name='法人号'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='environment',
            name='rdfa_list',
            field=models.CharField(default='20,30', max_length=50, verbose_name='虚拟RDFA列表'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='environment',
            name='zk_root_path',
            field=models.CharField(default='cn/onebank/gns/', max_length=50, verbose_name='zk的根地址'),
            preserve_default=False,
        ),
    ]
