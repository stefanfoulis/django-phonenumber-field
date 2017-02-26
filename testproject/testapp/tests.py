"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.db.models import Q
from django.test import TestCase


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
        self.assertEqual(str(tm.phone), '+41524242424')
        self.assertEqual(
            1,
            TestModel.objects
                .exclude(Q(phone__isnull=True) | Q(phone=''))
                .filter(pk=pk)
                .count())
        self.assertEqual(
            0,
            TestModel.objects
                .filter(Q(phone__isnull=True) | Q(phone=''))
                .filter(pk=pk)
                .count())

    def test_save_blank_phone_to_database(self):
        """Field Test for when Blank"""
        from testapp.models import TestModelPhoneB as TestModel
        tm = TestModel()
        tm.save()

        pk = tm.id
        tm = TestModel.objects.get(pk=pk)
        self.assertEqual(tm.phone, '')
        self.assertEqual(
            0,
            TestModel.objects
                .exclude(Q(phone__isnull=True) | Q(phone=''))
                .filter(pk=pk)
                .count())
        self.assertEqual(
            1,
            TestModel.objects
                .filter(Q(phone__isnull=True) | Q(phone=''))
                .filter(pk=pk)
                .count())

    def __test_nullable_field_helper(self, TestModel):
        """Helper method for the next four tests."""
        tm = TestModel()
        tm.save()

        pk = tm.id
        tm = TestModel.objects.get(pk=pk)
        self.assertIsNone(tm.phone)
        self.assertEqual(
            0,
            TestModel.objects
                .exclude(Q(phone__isnull=True) | Q(phone=''))
                .filter(pk=pk)
                .count())
        self.assertEqual(
            1,
            TestModel.objects
                .filter(Q(phone__isnull=True) | Q(phone=''))
                .filter(pk=pk)
                .count())

        # ensure that null values do not cause uniqueness conflicts
        self.assertEqual(TestModel.objects.count(), 1)
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
        self.assertEqual(str(tm.phone), '+41524242424')
        self.assertEqual(
            1,
            TestModel.objects
                .exclude(Q(phone__isnull=True) | Q(phone=''))
                .filter(pk=pk)
                .count())
        self.assertEqual(
            0,
            TestModel.objects
                .filter(Q(phone__isnull=True) | Q(phone=''))
                .filter(pk=pk)
                .count())

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
        self.assertEqual(tm.phone, '')
        self.assertEqual(
            0,
            TestModel.objects
                .exclude(Q(phone__isnull=True) | Q(phone=''))
                .filter(pk=pk)
                .count())
        self.assertEqual(
            1,
            TestModel.objects
                .filter(Q(phone__isnull=True) | Q(phone=''))
                .filter(pk=pk)
                .count())

    def test_save_unique_null_default_empty_phone_to_database(self):
        """Field Test for when Empty Default, Null & Unique"""
        from testapp.models import TestModelPhoneEDNU as TestModel
        self.__test_nullable_empty_default_field_helper(TestModel)

    def test_save_unique_null_blank_default_empty_phone_to_database(self):
        """Field Test for when Blank, Empty Default, Null & Unique"""
        from testapp.models import TestModelPhoneBEDNU as TestModel
        self.__test_nullable_empty_default_field_helper(TestModel)
