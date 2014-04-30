from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.


class TestModel(models.Model):
    name = models.CharField(max_length=255, blank=True, default='')
    phone = PhoneNumberField()
    
class TestModelBlankPhone(models.Model):
    name = models.CharField(max_length=255, blank=True, default='')
    phone = PhoneNumberField(blank=True)