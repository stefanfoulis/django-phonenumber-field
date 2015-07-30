from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from phonenumber_field.fields.models.caseinsensitivecharfield import CaseInsensitiveCharField

# Create your models here.


class TestModel(models.Model):
    name = models.CharField(max_length=255, blank=True, default='')
    phone = PhoneNumberField()

class TestModelBlankPhone(models.Model):
    name = models.CharField(max_length=255, blank=True, default='')
    phone = PhoneNumberField(blank=True)

class CICharFieldTestModel(models.Model):
    value = CaseInsensitiveCharField(primary_key=True, max_length=1)