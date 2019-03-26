# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import phonenumbers
from django import forms
from django.core import checks
from django.db.models import Model
from django.test import TestCase, override_settings
from django.utils.encoding import force_text
from phonenumbers import phonenumberutil

from phonenumber_field import formfields, modelfields
from phonenumber_field.modelfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber, to_python
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget

from . import models
from .forms import CustomPhoneNumberFormField, PhoneNumberForm


def phone_transform(obj):
    return (obj.pk, obj.name, obj.phone)


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
            models.MandatoryPhoneNumber.objects.create(
                phone_number=number_string
            ).phone_number
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
        model = models.OptionalPhoneNumber()
        self.assertEqual(model.phone_number, "")
        model.phone_number = "+49 176 96842671"
        self.assertEqual(type(model.phone_number), PhoneNumber)

    def test_null_field_returns_none(self):
        model = models.NullablePhoneNumber()
        self.assertEqual(model.phone_number, None)
        model.phone_number = self.test_number_1
        self.assertEqual(type(model.phone_number), PhoneNumber)
        model.phone_number = phonenumberutil.parse(
            self.test_number_1, keep_raw_input=True
        )
        self.assertEqual(type(model.phone_number), PhoneNumber)

    def test_can_assign_string_phone_number(self):
        opt_phone = models.OptionalPhoneNumber()
        opt_phone.phone_number = self.test_number_1
        self.assertEqual(type(opt_phone.phone_number), PhoneNumber)
        self.assertEqual(opt_phone.phone_number.as_e164, self.test_number_1)
        opt_phone.full_clean()
        opt_phone.save()
        self.assertEqual(type(opt_phone.phone_number), PhoneNumber)
        self.assertEqual(opt_phone.phone_number.as_e164, self.test_number_1)
        opt_phone_db = models.OptionalPhoneNumber.objects.get(id=opt_phone.id)
        self.assertEqual(type(opt_phone_db.phone_number), PhoneNumber)
        self.assertEqual(opt_phone_db.phone_number.as_e164, self.test_number_1)

    def test_can_assign_phonenumber(self):
        """
        Tests assignment phonenumberutil.PhoneNumber to field
        """
        opt_phone = models.OptionalPhoneNumber()
        opt_phone.phone_number = phonenumberutil.parse(
            self.test_number_1, keep_raw_input=True
        )
        self.assertEqual(type(opt_phone.phone_number), PhoneNumber)
        self.assertEqual(opt_phone.phone_number.as_e164, self.test_number_1)
        opt_phone.full_clean()
        opt_phone.save()
        self.assertEqual(type(opt_phone.phone_number), PhoneNumber)
        self.assertEqual(opt_phone.phone_number.as_e164, self.test_number_1)
        opt_phone_db = models.OptionalPhoneNumber.objects.get(id=opt_phone.id)
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


class PhonenumerFieldAppTest(TestCase):
    def test_save_field_to_database(self):
        """Basic Field Test"""
        tm = models.TestModel()
        tm.phone = "+41 52 424 2424"
        tm.full_clean()
        tm.save()
        pk = tm.id

        tm = models.TestModel.objects.get(pk=pk)
        self.assertIsInstance(tm.phone, PhoneNumber)
        self.assertQuerysetEqual(
            models.TestModel.objects.all(),
            [(tm.pk, "", "+41524242424")],
            transform=phone_transform,
        )

    def test_create_invalid_number(self):
        tm = models.TestModel.objects.create(phone="invalid")
        self.assertQuerysetEqual(
            models.TestModel.objects.all(), [(tm.pk, "", "")], transform=phone_transform
        )

    def test_save_invalid_number(self):
        tm = models.TestModel.objects.create(phone="+1 604-333-4444")

        tm.phone = "invalid"
        tm.save()

        self.assertQuerysetEqual(
            models.TestModel.objects.all(), [(tm.pk, "", "")], transform=phone_transform
        )

    def test_save_update_field_invalid_number(self):
        tm = models.TestModel.objects.create(phone="+1 604-333-4444")

        tm.phone = "invalid"
        tm.save(update_fields=["phone"])

        self.assertQuerysetEqual(
            models.TestModel.objects.all(), [(tm.pk, "", "")], transform=phone_transform
        )

    def test_update_to_invalid_number(self):
        tm = models.TestModel.objects.create(phone="+1 604-333-4444")

        models.TestModel.objects.update(phone="invalid")

        self.assertQuerysetEqual(
            models.TestModel.objects.all(), [(tm.pk, "", "")], transform=phone_transform
        )

    def test_save_blank_phone_to_database(self):
        """Field Test for when Blank"""
        tm = models.TestModelPhoneB()
        tm.save()

        pk = tm.id
        tm = models.TestModelPhoneB.objects.get(pk=pk)
        self.assertQuerysetEqual(
            models.TestModelPhoneB.objects.all(),
            [(tm.pk, "", "")],
            transform=phone_transform,
        )

    def __test_nullable_field_helper(self, TestModel):
        """Helper method for the next four tests."""
        tm = TestModel()
        tm.save()

        pk = tm.id
        tm = TestModel.objects.get(pk=pk)
        self.assertIsNone(tm.phone)
        self.assertQuerysetEqual(
            TestModel.objects.all(), [(tm.pk, "", None)], transform=phone_transform
        )

        # ensure that null values do not cause uniqueness conflicts
        TestModel.objects.create()
        self.assertEqual(TestModel.objects.count(), 2)

    def test_save_unique_null_phone_to_database(self):
        """Field Test for when Null & Unique"""
        self.__test_nullable_field_helper(models.TestModelPhoneNU)

    def test_save_unique_null_blank_phone_to_database(self):
        """Field Test for when Blank, Null & Unique"""
        self.__test_nullable_field_helper(models.TestModelPhoneBNU)

    def test_save_unique_null_none_phone_to_database(self):
        """Field Test for when No Default, Null & Unique"""
        self.__test_nullable_field_helper(models.TestModelPhoneNDNU)

    def test_save_unique_null_blank_none_phone_to_database(self):
        """Field Test for when Blank, No Default, Null & Unique"""
        self.__test_nullable_field_helper(models.TestModelPhoneBNDNU)

    def __test_nullable_default_field_helper(self, TestModel):
        """Helper method for the next two tests."""
        tm = TestModel()
        tm.save()

        pk = tm.id
        tm = TestModel.objects.get(pk=pk)
        self.assertQuerysetEqual(
            TestModel.objects.all(),
            [(tm.pk, "", "+41524242424")],
            transform=phone_transform,
        )

    def test_save_unique_null_default_phone_to_database(self):
        """Field Test for when Default, Null & Unique"""
        self.__test_nullable_default_field_helper(models.TestModelPhoneDNU)

    def test_save_unique_null_blank_default_phone_to_database(self):
        """Field Test for when Blank, Default, Null & Unique"""
        self.__test_nullable_default_field_helper(models.TestModelPhoneBDNU)

    def __test_nullable_empty_default_field_helper(self, TestModel):
        """Helper method for the next two tests."""
        tm = TestModel()
        tm.save()

        pk = tm.id
        tm = TestModel.objects.get(pk=pk)
        self.assertQuerysetEqual(
            TestModel.objects.all(), [(tm.pk, "", "")], transform=phone_transform
        )

    def test_save_unique_null_default_empty_phone_to_database(self):
        """Field Test for when Empty Default, Null & Unique"""
        self.__test_nullable_empty_default_field_helper(models.TestModelPhoneEDNU)

    def test_save_unique_null_blank_default_empty_phone_to_database(self):
        """Field Test for when Blank, Empty Default, Null & Unique"""
        self.__test_nullable_empty_default_field_helper(models.TestModelPhoneBEDNU)

    def test_model_attribute_can_be_accessed_on_class(self):
        self.assertIsInstance(models.TestModel.phone, modelfields.PhoneNumberDescriptor)


class RegionPhoneNumberFormFieldTest(TestCase):
    def test_regional_phone(self):
        class PhoneNumberForm(forms.Form):
            canadian_number = formfields.PhoneNumberField(region="CA")
            french_number = formfields.PhoneNumberField(region="FR")

        form = PhoneNumberForm(
            {"canadian_number": "604-686-2877", "french_number": "06 12 34 56 78"}
        )

        self.assertIs(form.is_valid(), True)
        self.assertEqual("+16046862877", form.cleaned_data["canadian_number"])
        self.assertEqual("+33612345678", form.cleaned_data["french_number"])

    def test_invalid_region(self):
        with self.assertRaises(ValueError) as cm:
            formfields.PhoneNumberField(region="invalid")

        self.assertTrue(
            force_text(cm.exception).startswith("“invalid” is not a valid region code.")
        )


class RegionPhoneNumberModelFieldTest(TestCase):
    def test_uses_region(self):
        m = models.FrenchPhoneOwner(cell_number="06 12 34 56 78")
        self.assertEqual(phonenumbers.parse("+33612345678"), m.cell_number)

    def test_accepts_international_numbers(self):
        num = "+16041234567"
        m = models.FrenchPhoneOwner(cell_number=num)
        self.assertEqual(phonenumbers.parse(num), m.cell_number)

    def test_formfield_uses_region(self):
        class FrenchPhoneForm(forms.ModelForm):
            class Meta:
                model = models.FrenchPhoneOwner
                fields = ["cell_number"]

        form = FrenchPhoneForm()
        self.assertEqual("FR", form.fields["cell_number"].region)

    def test_deconstruct_region(self):
        phone_field = modelfields.PhoneNumberField(region="CH")
        _name, path, args, kwargs = phone_field.deconstruct()
        self.assertEqual("phonenumber_field.modelfields.PhoneNumberField", path)
        self.assertEqual([], args)
        self.assertEqual({"max_length": 128, "region": "CH"}, kwargs)

    def test_deconstruct_no_region(self):
        phone_field = modelfields.PhoneNumberField()
        _name, path, args, kwargs = phone_field.deconstruct()
        self.assertEqual("phonenumber_field.modelfields.PhoneNumberField", path)
        self.assertEqual([], args)
        self.assertEqual({"max_length": 128, "region": None}, kwargs)

    def test_check_region(self):
        class InvalidRegionModel(Model):
            phone_field = modelfields.PhoneNumberField(region="invalid")

        errors = InvalidRegionModel.check()
        self.assertEqual(1, len(errors))
        error = errors[0]
        self.assertIsInstance(error, checks.Error)
        self.assertTrue(error.msg.startswith("“invalid” is not a valid region code."))
        self.assertEqual(error.obj, InvalidRegionModel._meta.get_field("phone_field"))

    def test_override_form_field(self):
        phone_number = models.CustomPhoneNumber()
        model_field = phone_number._meta.get_field("phone_number")
        self.assertIsInstance(model_field.formfield(), CustomPhoneNumberFormField)
