from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from phonenumber_field.fields.models.caseinsensitivecharfield import CaseInsensitiveCharField

###############
# Test Models #
###############

class MandatoryPhoneNumber(models.Model):
    phone_number = PhoneNumberField()


class OptionalPhoneNumber(models.Model):
    phone_number = PhoneNumberField(blank=True, default='')


class CICharFieldTestModel(models.Model):
    value = CaseInsensitiveCharField(primary_key=True, max_length=1)