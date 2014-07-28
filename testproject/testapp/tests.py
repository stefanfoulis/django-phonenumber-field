"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.conf import settings


class PhonenumerFieldAppTest(TestCase):
    def test_save_field_to_database(self):
        from testapp.models import TestModel
        from phonenumber_field.phonenumber import PhoneNumber
        tm = TestModel()
        tm.phone = '+41 52 424 2424'
        tm.full_clean()
        tm.save()
        pk = tm.id

        tm = TestModel.objects.get(pk=pk)
        self.assertTrue(isinstance(tm.phone, PhoneNumber))
        self.assertEqual(str(tm.phone), '+41524242424')

    def test_save_blank_phone_to_database(self):
        from testapp.models import TestModelBlankPhone
        from phonenumber_field.phonenumber import PhoneNumber
        tm = TestModelBlankPhone()
        tm.save()

        pk = tm.id
        tm = TestModelBlankPhone.objects.get(pk=pk)
        self.assertIsNone(tm.phone)

    def test_settings_format(self):
        from testapp.models import TestModel
        settings.PHONENUMBER_DEFAULT_REGION = 'US'
        settings.PHONENUMBER_DEFAULT_FORMAT = 'NATIONAL'
        tm = TestModel()
        tm.phone = '(234) 567-8901'
        tm.full_clean()
        tm.save()
        pk = tm.id
        tm = TestModel.objects.get(pk=pk)
        self.assertEqual(str(tm.phone), '(234) 567-8901')

    def test_settings_serialize(self):
        # The E164 serialization format doesn't include extensions. By testing that our extension
        # is still there, we test that the serialization setting actually works.
        from testapp.models import TestModel
        settings.PHONENUMBER_DEFAULT_REGION = 'US'
        settings.PHONENUMBER_DEFAULT_FORMAT = 'NATIONAL'
        settings.PHONENUMBER_SERIALIZE_FORMAT = 'NATIONAL'
        tm = TestModel()
        tm.phone = '(234) 567-8901 ext. 123'
        tm.full_clean()
        tm.save()
        pk = tm.id
        tm = TestModel.objects.get(pk=pk)
        self.assertEqual(str(tm.phone), '(234) 567-8901 ext. 123')
