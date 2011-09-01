#-*- coding: utf-8 -*-
from django.test.testcases import TestCase
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber
import phonenumber_field


###############
# Test Models #
###############


class MandatoryPhoneNumber(models.Model):
    phone_number = PhoneNumberField()


class OptionalPhoneNumber(models.Model):
    phone_number = PhoneNumberField(blank=True, default='')


class NullablePhoneNumber(models.Model):
    phone_number = PhoneNumberField(blank=True, null=True)


##############
# Test Cases #
##############


class PhoneNumberFieldTestCase(TestCase):
    test_number_1 = '+414204242'

    def create_fixtures(self):
        self.mandatory = MandatoryPhoneNumber(phone_number=self.test_number_1)
        self.mandatory.save()

    def test_can_create_model_with_string(self):
        obj = MandatoryPhoneNumber.objects.create(phone_number=self.test_number_1)
        # refetch it
        obj2 = MandatoryPhoneNumber.objects.get(pk=obj.pk)
        self.assertEqual(obj.phone_number, obj2.phone_number)

    def test_can_assign_string_phone_number(self):
        opt_phone = OptionalPhoneNumber()
        opt_phone.phone_number = self.test_number_1

        self.assertEqual(type(opt_phone.phone_number), PhoneNumber)
        self.assertEqual(opt_phone.phone_number.as_e164, self.test_number_1)