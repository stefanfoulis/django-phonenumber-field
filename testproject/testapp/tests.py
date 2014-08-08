"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
try:
    from django.db.transaction import atomic
except ImportError:
    from django.db.transaction import commit_on_success as atomic
from django.db.utils import IntegrityError

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
        tm = TestModelBlankPhone()
        tm.save()
        
        pk = tm.id
        tm = TestModelBlankPhone.objects.get(pk=pk)
        self.assertIsNone(tm.phone)

    def test_default(self):
        from testapp.models import TestModelDefaultPhone
        tm = TestModelDefaultPhone.objects.create()
        self.assertEqual(str(tm.phone), '+41524242424')

    def test_save_blank_or_unique(self):
        from testapp.models import TestModelBlankAndUniquePhone

        tm_nullable1 = TestModelBlankAndUniquePhone.objects.create()
        self.assertIsNone(tm_nullable1.phone)
        tm_nullable2 = TestModelBlankAndUniquePhone.objects.create()
        self.assertIsNone(tm_nullable2.phone)

        tm_unique = TestModelBlankAndUniquePhone.objects.create(phone='+41 52 424 2424')
        self.assertEqual(str(tm_unique.phone), '+41524242424')
        with self.assertRaises(IntegrityError):
            with atomic():
                TestModelBlankAndUniquePhone.objects.create(phone='+41524242424')

        self.assertEqual(TestModelBlankAndUniquePhone.objects.count(), 3)

