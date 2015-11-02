# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.test import TestCase

from phonenumber_field.phonenumber import PhoneNumber

from .models import TestModel, TestModelBlankPhone


class PhoneNumberFieldAppTest(TestCase):

    def test_save_field_to_database(self):
        tm = TestModel()
        tm.phone = '+41 52 424 2424'
        tm.full_clean()
        tm.save()
        pk = tm.id

        tm = TestModel.objects.get(pk=pk)
        self.assertTrue(isinstance(tm.phone, PhoneNumber))
        self.assertEqual(str(tm.phone), '+41524242424')

    def test_save_blank_phone_to_database(self):
        tm = TestModelBlankPhone()
        tm.save()

        pk = tm.id
        tm = TestModelBlankPhone.objects.get(pk=pk)
        self.assertEqual(tm.phone, '')
