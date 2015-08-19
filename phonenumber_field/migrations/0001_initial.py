# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import phonenumber_field.fields.models.caseinsensitivecharfield


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CallingCode',
            fields=[
                ('code', models.PositiveSmallIntegerField(serialize=False, primary_key=True, validators=[django.core.validators.MinValueValidator(1)])),
                ('active', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('code',),
            },
        ),
        migrations.CreateModel(
            name='CountryCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.BooleanField(default=False)),
                ('calling_code_obj', models.ForeignKey(related_name='country_codes', to='phonenumber_field.CallingCode')),
            ],
            options={
                'ordering': ('region_code_obj', 'calling_code_obj'),
            },
        ),
        migrations.CreateModel(
            name='RegionCode',
            fields=[
                ('code', phonenumber_field.fields.models.caseinsensitivecharfield.CaseInsensitiveCharField(max_length=2, serialize=False, primary_key=True)),
                ('active', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('code',),
            },
        ),
        migrations.AddField(
            model_name='countrycode',
            name='region_code_obj',
            field=models.OneToOneField(related_name='country_code', null=True, blank=True, to='phonenumber_field.RegionCode'),
        ),
        migrations.AlterUniqueTogether(
            name='countrycode',
            unique_together=set([('region_code_obj', 'calling_code_obj')]),
        ),
    ]
