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
        self.assertEqual(tm.phone, '')

    def test_save_phone_to_database_with_phone_number_prefix_widget(self):
        from testapp.forms import TestFormWidget
        from testapp.models import TestModelBlankPhone
        tf = TestFormWidget(data={'phone_0': '+374', 'phone_1': '94123456'})
        self.assertTrue(tf.is_valid())

        tm = tf.save()

        pk = tm.id
        tm = TestModelBlankPhone.objects.get(pk=pk)
        self.assertEqual(tm.phone, '+37494123456')

    def test_wrong_phone_save_to_database_with_phone_number_prefix_widget_fail(self):
        from testapp.forms import TestFormWidget
        from testapp.models import TestModelBlankPhone
        tf = TestFormWidget(data={'phone_0': '+3', 'phone_1': '94123456'})
        self.assertFalse(tf.is_valid())

    def test_save_blank_phone_to_database_with_phone_number_prefix_widget(self):
        from testapp.forms import TestFormWidget
        from testapp.models import TestModelBlankPhone
        tf = TestFormWidget(data={'phone_0': '', 'phone_1': ''})
        self.assertTrue(tf.is_valid())

        tm = tf.save()

        pk = tm.id
        tm = TestModelBlankPhone.objects.get(pk=pk)
        self.assertEqual(tm.phone, '')

