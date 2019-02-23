# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.db import models
from django.test import override_settings
from django.test.testcases import TestCase

import phonenumbers
from phonenumbers import phonenumberutil

from phonenumber_field.modelfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber, to_python
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget

###############
# Test Models #
###############


class MandatoryPhoneNumber(models.Model):
    phone_number = PhoneNumberField()


class OptionalPhoneNumber(models.Model):
    phone_number = PhoneNumberField(blank=True, default="")


class NullablePhoneNumber(models.Model):
    phone_number = PhoneNumberField(blank=True, null=True)


class PhoneNumberForm(forms.ModelForm):
    class Meta:
        model = NullablePhoneNumber
        fields = ("phone_number",)


##############
# Test Cases #
##############


class PhoneNumberFieldTestCase(TestCase):
    test_number_1 = "+4930123456"
    equal_number_strings = ["+44 113 8921113", "+441138921113", "tel:+44-113-892-1113"]
    local_numbers = [("GB", "01606 751 78"), ("DE", "0176/96842671")]
    storage_numbers = {
        "E164": ["+44 113 8921113", "+441138921113"],
        "RFC3966": ["+44 113 8921113", "tel:+44-113-892-1113"],
        "INTERNATIONAL": ["+44 113 8921113", "+44 113 892 1113"],
    }
    invalid_numbers = ["+44 113 892111"]

    def test_valid_numbers_are_valid(self):
        numbers = [
            PhoneNumber.from_string(number_string)
            for number_string in self.equal_number_strings
        ]
        self.assertTrue(all(number.is_valid() for number in numbers))
        numbers = [
            PhoneNumber.from_string(number_string, region=region)
            for region, number_string in self.local_numbers
        ]
        self.assertTrue(all(number.is_valid() for number in numbers))

    def test_invalid_numbers_are_invalid(self):
        numbers = [
            PhoneNumber.from_string(number_string)
            for number_string in self.invalid_numbers
        ]
        self.assertTrue(all(not number.is_valid() for number in numbers))

    def test_objects_with_same_number_are_equal(self):
        numbers = [
            MandatoryPhoneNumber.objects.create(phone_number=number_string).phone_number
            for number_string in self.equal_number_strings
        ]
        self.assertTrue(
            all(
                phonenumbers.is_number_match(n, numbers[0])
                == phonenumbers.MatchType.EXACT_MATCH
                for n in numbers
            )
        )
        for number in numbers:
            self.assertEqual(number, numbers[0])
            for number_string in self.equal_number_strings:
                self.assertEqual(number, number_string)

    def test_same_number_has_same_hash(self):
        numbers = [
            PhoneNumber.from_string(number_string)
            for number_string in self.equal_number_strings
        ]
        numbers_set = set(numbers)
        self.assertEqual(len(numbers_set), 1)
        for number in numbers:
            self.assertIn(number, numbers_set)
        self.assertNotIn(self.test_number_1, numbers_set)

    def test_eq_and_ne(self):
        number_1 = "+411111111"
        number_2 = "+412222222"
        one = PhoneNumber.from_string("+411111111")
        two = PhoneNumber.from_string("+412222222")
        self.assertNotEqual(one, two)
        self.assertNotEqual(one, number_2)
        self.assertNotEqual(number_2, one)
        self.assertEqual(one, number_1)
        self.assertEqual(number_1, one)

    def test_blank_field_returns_empty_string(self):
        model = OptionalPhoneNumber()
        self.assertEqual(model.phone_number, "")
        model.phone_number = "+49 176 96842671"
        self.assertEqual(type(model.phone_number), PhoneNumber)

    def test_null_field_returns_none(self):
        model = NullablePhoneNumber()
        self.assertEqual(model.phone_number, None)
        model.phone_number = self.test_number_1
        self.assertEqual(type(model.phone_number), PhoneNumber)
        model.phone_number = phonenumberutil.parse(
            self.test_number_1, keep_raw_input=True
        )
        self.assertEqual(type(model.phone_number), PhoneNumber)

    def test_can_assign_string_phone_number(self):
        opt_phone = OptionalPhoneNumber()
        opt_phone.phone_number = self.test_number_1
        self.assertEqual(type(opt_phone.phone_number), PhoneNumber)
        self.assertEqual(opt_phone.phone_number.as_e164, self.test_number_1)
        opt_phone.full_clean()
        opt_phone.save()
        self.assertEqual(type(opt_phone.phone_number), PhoneNumber)
        self.assertEqual(opt_phone.phone_number.as_e164, self.test_number_1)
        opt_phone_db = OptionalPhoneNumber.objects.get(id=opt_phone.id)
        self.assertEqual(type(opt_phone_db.phone_number), PhoneNumber)
        self.assertEqual(opt_phone_db.phone_number.as_e164, self.test_number_1)

    def test_can_assign_phonenumber(self):
        """
        Tests assignment phonenumberutil.PhoneNumber to field
        """
        opt_phone = OptionalPhoneNumber()
        opt_phone.phone_number = phonenumberutil.parse(
            self.test_number_1, keep_raw_input=True
        )
        self.assertEqual(type(opt_phone.phone_number), PhoneNumber)
        self.assertEqual(opt_phone.phone_number.as_e164, self.test_number_1)
        opt_phone.full_clean()
        opt_phone.save()
        self.assertEqual(type(opt_phone.phone_number), PhoneNumber)
        self.assertEqual(opt_phone.phone_number.as_e164, self.test_number_1)
        opt_phone_db = OptionalPhoneNumber.objects.get(id=opt_phone.id)
        self.assertEqual(type(opt_phone_db.phone_number), PhoneNumber)
        self.assertEqual(opt_phone_db.phone_number.as_e164, self.test_number_1)

    def test_does_not_fail_on_invalid_values(self):
        # testcase for
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

    @override_settings(PHONENUMBER_DEFAULT_REGION="DE")
    def test_storage_formats(self):
        """
        Perform aggregate tests for all db storage formats
        """
        for frmt in PhoneNumber.format_map:
            with override_settings(PHONENUMBER_DB_FORMAT=frmt):
                self._test_storage_formats()

    def test_prep_value(self):
        """
        Tests correct db storage value against different setting of
        PHONENUMBER_DB_FORMAT
        Required output format is set as string constant to guarantee
        consistent database storage values
        """
        number = PhoneNumberField()
        for frmt in ["E164", "RFC3966", "INTERNATIONAL"]:
            with override_settings(PHONENUMBER_DB_FORMAT=frmt):
                self.assertEqual(
                    number.get_prep_value(to_python(self.storage_numbers[frmt][0])),
                    self.storage_numbers[frmt][1],
                )

    def test_fallback_widget_switches_between_national_and_international(self):
        region, number_string = self.local_numbers[0]
        number = PhoneNumber.from_string(number_string, region=region)
        gb_widget = PhoneNumberInternationalFallbackWidget(region="GB")
        de_widget = PhoneNumberInternationalFallbackWidget(region="DE")
        self.assertHTMLEqual(
            gb_widget.render("number", number),
            '<input name="number" type="text" value="01606 75178" />',
        )
        self.assertHTMLEqual(
            de_widget.render("number", number),
            '<input name="number" type="text" value="+44 1606 75178" />',
        )

        # If there's been a validation error, the value should be included verbatim
        self.assertHTMLEqual(
            gb_widget.render("number", "error"),
            '<input name="number" type="text" value="error" />',
        )

    def test_phone_number_form_empty_value(self):
        form = PhoneNumberForm({"phone_number": ""})

        self.assertTrue(form.is_valid())
        self.assertDictEqual({"phone_number": None}, form.cleaned_data)
