# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-10-01 22:41
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('packagedb', '0013_auto_20181001_1209'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='package',
            name='package_url',
        ),
    ]