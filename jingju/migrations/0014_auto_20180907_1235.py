# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-09-07 10:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jingju', '0013_auto_20180906_1712'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artist',
            name='role_type',
            field=models.ManyToManyField(to='jingju.RoleType'),
        ),
    ]