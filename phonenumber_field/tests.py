# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import phonenumbers
from phonenumbers import phonenumberutil

from django.conf import settings
from django.db import models
from django.test.testcases import TestCase

from .modelfields import PhoneNumberField
from .phonenumber import PhoneNumber, to_python


###############
# Test Models #
###############

class MandatoryPhoneNumber(models.Model):
    phone_number = PhoneNumberField()


class OptionalPhoneNumber(models.Model):
    phone_number = PhoneNumberField(blank=True, default='')


class NullablePhoneNumber(models.Model):
    phone_number = PhoneNumberField(null=True)


##############
# Test Cases #
##############

class PhoneNumberFieldTestCase(TestCase):
    test_number_1 = '+414204242'
    equal_number_strings = [
        '+44 113 8921113',
        '+441138921113',
    ]
    local_numbers = [
        ('GB', '01606 751 78'),
        ('DE', '0176/96842671'),
    ]
    storage_numbers = {
        'E164': [
            '+44 113 8921113',
            '+441138921113',
        ],
        'RFC3966': [
            '+44 113 8921113',
            'tel:+44-113-892-1113',
        ],
        'INTERNATIONAL': [
            '+44 113 8921113',
            '+44 113 892 1113',
        ],
    }
    invalid_numbers = ['+44 113 892111']

    def test_valid_numbers_are_valid(self):
        numbers = [
            PhoneNumber.from_string(number_string)
            for number_string
            in self.equal_number_strings
        ]
        self.assertTrue(all([number.is_valid() for number in numbers]))

        numbers = [
            PhoneNumber.from_string(number_string, region=region)
            for region, number_string
            in self.local_numbers
        ]
        self.assertTrue(all([number.is_valid() for number in numbers]))

    def test_invalid_numbers_are_invalid(self):
        numbers = [
            PhoneNumber.from_string(number_string)
            for number_string
            in self.invalid_numbers
        ]
        self.assertTrue(all([not number.is_valid() for number in numbers]))

    def test_objects_with_same_number_are_equal(self):
        numbers = [
            MandatoryPhoneNumber.objects.create(phone_number=number_string).phone_number
            for number_string
            in self.equal_number_strings
        ]
        self.assertTrue(
            all(
                phonenumbers.is_number_match(n, numbers[0]) == phonenumbers.MatchType.EXACT_MATCH
                for n
                in numbers
            )
        )

    def test_blank_field_returns_empty_string(self):
        model = OptionalPhoneNumber()
        self.assertEqual(model.phone_number, '')
        model.phone_number = '+49 176 96842671'
        self.assertEqual(type(model.phone_number), PhoneNumber)
        
    def test_null_field_returns_none(self):
        model = NullablePhoneNumber()
        self.assertEqual(model.phone_number, None)
        model.phone_number = '+49 176 96842671'
        self.assertEqual(type(model.phone_number), PhoneNumber)
        model.phone_number = phonenumberutil.parse(
            self.test_number_1, keep_raw_input=True)
        self.assertEqual(type(model.phone_number), PhoneNumber)

    def test_can_assign_string_phone_number(self):
        opt_phone = OptionalPhoneNumber()
        opt_phone.phone_number = self.test_number_1
        self.assertEqual(type(opt_phone.phone_number), PhoneNumber)
        self.assertEqual(opt_phone.phone_number.as_e164, self.test_number_1)

    def test_can_assign_phonenumber(self):
        """
        Tests assignment phonenumberutil.PhoneNumber to field
        """
        opt_phone = OptionalPhoneNumber()
        opt_phone.phone_number = phonenumberutil.parse(
            self.test_number_1, keep_raw_input=True)
        self.assertEqual(type(opt_phone.phone_number), PhoneNumber)
        self.assertEqual(opt_phone.phone_number.as_e164, self.test_number_1)

    def test_does_not_fail_on_invalid_values(self):
        # Test for issue
        # https://github.com/stefanfoulis/django-phonenumber-field/issues/11
        phone = to_python(42)
        self.assertEqual(phone, None)

    def _test_storage_formats(self):
        """
        Aggregate of tests to perform for db storage formats
        """
        self.test_objects_with_same_number_are_equal()
        self.test_blank_field_returns_empty_string()
        self.test_null_field_returns_none()
        self.test_can_assign_string_phone_number()

    def test_storage_formats(self):
        """
        Perform aggregate tests for all db storage formats
        """
        old_format = getattr(settings, 'PHONENUMBER_DB_FORMAT', 'E164')
        for frmt in PhoneNumber.format_map:
            setattr(settings, 'PHONENUMBER_DB_FORMAT', frmt)
            self._test_storage_formats()
        setattr(settings, 'PHONENUMBER_DB_FORMAT', old_format)

    def test_prep_value(self):
        """
        Tests correct db storage value against different setting of
        PHONENUMBER_DB_FORMAT
        Required output format is set as string constant to guarantee
        consistent database storage values
        """
        number = PhoneNumberField()
        old_format = getattr(settings, 'PHONENUMBER_DB_FORMAT', 'E164')
        for frmt in ['E164', 'RFC3966', 'INTERNATIONAL']:
            setattr(settings, 'PHONENUMBER_DB_FORMAT', frmt)
            self.assertEqual(
                number.get_prep_value(
                    to_python(self.storage_numbers[frmt][0])
                ),
                self.storage_numbers[frmt][1])
        setattr(settings, 'PHONENUMBER_DB_FORMAT', old_format)
