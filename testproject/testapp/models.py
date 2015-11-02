# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class TestModel(models.Model):
    name = models.CharField(max_length=255, blank=True, default='')
    phone = PhoneNumberField()


class TestModelBlankPhone(models.Model):
    name = models.CharField(max_length=255, blank=True, default='')
    phone = PhoneNumberField(blank=True)
