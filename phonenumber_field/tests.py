# -*- coding: utf-8 -*-


import phonenumbers
from django import forms
from django.conf import settings
from django.db import models
from django.test import TestCase
from django.test.utils import override_settings
from phonenumbers import phonenumberutil

from phonenumber_field.modelfields import PhoneNumberField
from phonenumber_field.formfields import PhoneNumberRegionFallbackField
from phonenumber_field.phonenumber import PhoneNumber, to_python
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget


###############
# Test Models #
###############

class MandatoryPhoneNumber(models.Model):
    phone_number = PhoneNumberField()


class OptionalPhoneNumber(models.Model):
    phone_number = PhoneNumberField(blank=True)


class NullablePhoneNumber(models.Model):
    phone_number = PhoneNumberField(null=True)


##############
# Test Cases #
##############


class PhoneNumberFieldTestCase(TestCase):
    test_number_1 = '+4930123456'
    equal_number_strings = [
        '+44 113 8921113',
        '+441138921113',
        'tel:+44-113-892-1113',
    ]
    local_numbers = [
        ('GB', '01606 751 78'),
        ('DE', '0176/96842671'),
    ]
    storage_numbers = {
        'E164': ['+44 113 8921113', '+441138921113'],
        'RFC3966': ['+44 113 8921113', 'tel:+44-113-892-1113'],
        'INTERNATIONAL': ['+44 113 8921113', '+44 113 892 1113'],
    }
    invalid_numbers = ['+44 113 892111', ]

    def test_valid_numbers_are_valid(self):
        numbers = [PhoneNumber.from_string(number_string)
                   for number_string in self.equal_number_strings]
        self.assertTrue(all(number.is_valid() for number in numbers))
        numbers = [PhoneNumber.from_string(number_string, region=region)
                   for region, number_string in self.local_numbers]
        self.assertTrue(all(number.is_valid() for number in numbers))

    def test_invalid_numbers_are_invalid(self):
        numbers = [PhoneNumber.from_string(number_string)
                   for number_string in self.invalid_numbers]
        self.assertTrue(all(not number.is_valid() for number in numbers))

    def test_objects_with_same_number_are_equal(self):
        numbers = [
            MandatoryPhoneNumber.objects.create(
                phone_number=number_string).phone_number
            for number_string in self.equal_number_strings]
        self.assertTrue(
            all(phonenumbers.is_number_match(n, numbers[0]) ==
                phonenumbers.MatchType.EXACT_MATCH for n in numbers))
        for number in numbers:
            self.assertEqual(number, numbers[0])
            for number_string in self.equal_number_strings:
                self.assertEqual(number, number_string)

    def test_same_number_has_same_hash(self):
        numbers = [PhoneNumber.from_string(number_string)
                   for number_string in self.equal_number_strings]
        numbers_set = set(numbers)
        self.assertEqual(len(numbers_set), 1)
        for number in numbers:
            self.assertIn(number, numbers_set)
        self.assertNotIn(self.test_number_1, numbers_set)

    def test_blank_field_returns_empty_string(self):
        model = OptionalPhoneNumber()
        self.assertEqual(model.phone_number, '')
        model.phone_number = '+49 176 96842671'
        self.assertEqual(type(model.phone_number), PhoneNumber)

        form_class = forms.models.modelform_factory(OptionalPhoneNumber, fields=['phone_number'])
        form = form_class({})
        form.is_valid()
        self.assertEqual('', form.cleaned_data['phone_number'])

    def test_null_field_returns_none(self):
        model = NullablePhoneNumber()
        self.assertEqual(model.phone_number, None)
        model.phone_number = self.test_number_1
        self.assertEqual(type(model.phone_number), PhoneNumber)
        model.phone_number = phonenumberutil.parse(
            self.test_number_1, keep_raw_input=True)
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

    @override_settings(PHONENUMBER_DEFAULT_REGION='DE')
    def test_fallback_field(self):
        local_number = PhoneNumber.from_string(self.local_numbers[1][1], region='DE')
        foreign_number = PhoneNumber.from_string(self.local_numbers[0][1], region='GB')

        class FallbackForm(forms.Form):
            local_number_field = PhoneNumberRegionFallbackField()
            foreign_number_field = PhoneNumberRegionFallbackField(region='GB')

        # Show and parse national numbers without region code.
        form = FallbackForm({
            'local_number_field': local_number,
            'foreign_number_field': foreign_number,
        })
        self.assertTrue(any('local_number_field' in l and local_number.as_national in l
                            for l in form.as_p().splitlines()))
        self.assertTrue(any('foreign_number_field' in l and foreign_number.as_national in l
                            for l in form.as_p().splitlines()))
        self.assertEqual(local_number, form.cleaned_data['local_number_field'])
        self.assertEqual(foreign_number, form.cleaned_data['foreign_number_field'])

        # Show and parse international numbers with region code.
        form = FallbackForm({
            'local_number_field': foreign_number,
            'foreign_number_field': local_number,
        })
        self.assertTrue(any('local_number_field' in l and foreign_number.as_international in l
                            for l in form.as_p().splitlines()))
        self.assertTrue(any('foreign_number_field' in l and local_number.as_international in l
                            for l in form.as_p().splitlines()))
        self.assertEqual(foreign_number, form.cleaned_data['local_number_field'])
        self.assertEqual(local_number, form.cleaned_data['foreign_number_field'])

        # Do not tamper with user input when re-displaying the form.
        form = FallbackForm({
            'local_number_field': 'foo',
            'foreign_number_field': 'bar',
        })
        self.assertTrue(any('local_number_field' in l and '"foo"' in l
                            for l in form.as_p().splitlines()))
        self.assertTrue(any('foreign_number_field' in l and '"bar"' in l
                            for l in form.as_p().splitlines()))

        form = FallbackForm({'local_number_field': ''})
        form.fields['local_number_field'].required = False
        form.is_valid()
        self.assertEqual('', form.cleaned_data['local_number_field'])

    def test_fallback_widget_switches_between_national_and_international(self):
        region, number_string = self.local_numbers[0]
        number = PhoneNumber.from_string(number_string, region=region)
        gb_widget = PhoneNumberInternationalFallbackWidget(region='GB')
        de_widget = PhoneNumberInternationalFallbackWidget(region='DE')
        self.assertHTMLEqual(
            gb_widget.render("number", number),
            u'<input name="number" type="text" value="01606 75178" />'
        )
        self.assertHTMLEqual(
            de_widget.render("number", number),
            u'<input name="number" type="text" value="+44 1606 75178" />'
        )

        # If there's been a validation error, the value should be included verbatim
        self.assertHTMLEqual(
            gb_widget.render("number", "error"),
            u'<input name="number" type="text" value="error" />'
        )
