"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase


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

    def test_save_phone_ext_to_database_with_rfc(self):
        from testapp.models import TestModelRfc
        from phonenumber_field.phonenumber import PhoneNumber
        tm = TestModelRfc()
        tm.phone = '+86 0451 8450 2510 x231'
        tm.full_clean()
        tm.save()
        pk = tm.id

        tm = TestModelRfc.objects.get(pk=pk)
        self.assertTrue(isinstance(tm.phone, PhoneNumber))
        self.assertEqual(tm.phone.extension, '231')
        self.assertEqual(tm.phone.as_international, '+86 451 8450 2510 ext. 231')
