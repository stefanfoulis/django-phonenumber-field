from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class TestModel(models.Model):
    name = models.CharField(max_length=255, blank=True, default='')
    phone = PhoneNumberField()


class TestModelBlankPhone(models.Model):
    name = models.CharField(max_length=255, blank=True, default='')
    phone = PhoneNumberField(blank=True)


class TestModelDefaultPhone(models.Model):
    name = models.CharField(max_length=255, blank=True, default='')
    phone = PhoneNumberField(default='+41 52 424 2424')


class TestModelBlankAndUniquePhone(models.Model):
    name = models.CharField(max_length=255, blank=True, default='')
    phone = PhoneNumberField(blank=True, null=True, unique=True)