# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-08-20 15:44
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("experiments", "0017_experiment_type")]

    operations = [
        migrations.AlterField(
            model_name="experimentvariant",
            name="value",
            field=django.contrib.postgres.fields.jsonb.JSONField(
                blank=True, null=True
            ),
        ),
        migrations.AlterUniqueTogether(
            name="experimentvariant",
            unique_together=set([("slug", "experiment")]),
        ),
    ]
