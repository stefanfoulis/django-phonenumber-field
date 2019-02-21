# -*- coding: utf-8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from __future__ import unicode_literals

from django import forms
from django.core import checks
from django.db.models import Model, Q
from django.utils.encoding import force_text
from django.test import TestCase

import phonenumbers

from . import models
from phonenumber_field import formfields, modelfields


def phone_transform(obj):
    return (obj.pk, obj.name, obj.phone)


class PhonenumerFieldAppTest(TestCase):
    def test_save_field_to_database(self):
        """Basic Field Test"""
        from testapp.models import TestModel
        from phonenumber_field.phonenumber import PhoneNumber
        tm = TestModel()
        tm.phone = '+41 52 424 2424'
        tm.full_clean()
        tm.save()
        pk = tm.id

        tm = TestModel.objects.get(pk=pk)
        self.assertTrue(isinstance(tm.phone, PhoneNumber))
        self.assertQuerysetEqual(
            TestModel.objects.all(),
            [(tm.pk, "", "+41524242424")],
            transform=phone_transform,
        )

    def test_save_blank_phone_to_database(self):
        """Field Test for when Blank"""
        from testapp.models import TestModelPhoneB as TestModel
        tm = TestModel()
        tm.save()

        pk = tm.id
        tm = TestModel.objects.get(pk=pk)
        self.assertQuerysetEqual(
            TestModel.objects.all(), [(tm.pk, "", "")], transform=phone_transform,
        )

    def __test_nullable_field_helper(self, TestModel):
        """Helper method for the next four tests."""
        tm = TestModel()
        tm.save()

        pk = tm.id
        tm = TestModel.objects.get(pk=pk)
        self.assertIsNone(tm.phone)
        self.assertQuerysetEqual(
            TestModel.objects.all(), [(tm.pk, "", None)], transform=phone_transform,
        )

        # ensure that null values do not cause uniqueness conflicts
        TestModel.objects.create()
        self.assertEqual(TestModel.objects.count(), 2)

    def test_save_unique_null_phone_to_database(self):
        """Field Test for when Null & Unique"""
        from testapp.models import TestModelPhoneNU as TestModel
        self.__test_nullable_field_helper(TestModel)

    def test_save_unique_null_blank_phone_to_database(self):
        """Field Test for when Blank, Null & Unique"""
        from testapp.models import TestModelPhoneBNU as TestModel
        self.__test_nullable_field_helper(TestModel)

    def test_save_unique_null_none_phone_to_database(self):
        """Field Test for when No Default, Null & Unique"""
        from testapp.models import TestModelPhoneNDNU as TestModel
        self.__test_nullable_field_helper(TestModel)

    def test_save_unique_null_blank_none_phone_to_database(self):
        """Field Test for when Blank, No Default, Null & Unique"""
        from testapp.models import TestModelPhoneBNDNU as TestModel
        self.__test_nullable_field_helper(TestModel)

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
        from testapp.models import TestModelPhoneDNU as TestModel
        self.__test_nullable_default_field_helper(TestModel)

    def test_save_unique_null_blank_default_phone_to_database(self):
        """Field Test for when Blank, Default, Null & Unique"""
        from testapp.models import TestModelPhoneBDNU as TestModel
        self.__test_nullable_default_field_helper(TestModel)

    def __test_nullable_empty_default_field_helper(self, TestModel):
        """Helper method for the next two tests."""
        tm = TestModel()
        tm.save()

        pk = tm.id
        tm = TestModel.objects.get(pk=pk)
        self.assertQuerysetEqual(
            TestModel.objects.all(), [(tm.pk, "", "")], transform=phone_transform,
        )

    def test_save_unique_null_default_empty_phone_to_database(self):
        """Field Test for when Empty Default, Null & Unique"""
        from testapp.models import TestModelPhoneEDNU as TestModel
        self.__test_nullable_empty_default_field_helper(TestModel)

    def test_save_unique_null_blank_default_empty_phone_to_database(self):
        """Field Test for when Blank, Empty Default, Null & Unique"""
        from testapp.models import TestModelPhoneBEDNU as TestModel
        self.__test_nullable_empty_default_field_helper(TestModel)

    def test_model_attribute_can_be_accessed_on_class(self):
        from testapp.models import TestModel
        from phonenumber_field.modelfields import PhoneNumberDescriptor
        self.assertIsInstance(TestModel.phone, PhoneNumberDescriptor)


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
