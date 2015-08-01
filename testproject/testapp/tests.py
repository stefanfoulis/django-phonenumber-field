"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.conf import settings
from django.test import TestCase

class PhonenumerFieldAppTest(TestCase):
    def test_to_python_country_id_parse(self):
        from phonenumber_field.phonenumber import PhoneNumber, to_python
        value = PhoneNumber.region_code_sep.join(["CH", "+41524242424"])
        p = to_python(value)
        self.assertEqual(p.region_code, "CH")
        
        p = to_python("+41524242424")
        self.assertIsNone(p.region_code)

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
        self.assertIsNone(tm.phone.region_code)
        
        tm.phone = PhoneNumber.region_code_sep.join(["CH", str(tm.phone)])
        tm.save()
        
        tm = TestModel.objects.get(pk=pk)
        self.assertEqual(tm.phone.region_code, "CH")
        
        tm.phone.extension = "777"
        tm.save()
        
        tm = TestModel.objects.get(pk=pk)
        self.assertEqual(str(tm.phone.extension), "777")
        self.assertEqual(str(tm.phone), '+41524242424x777')
    
    def test_save_blank_phone_to_database(self):
        from testapp.models import TestModelBlankPhone
        from phonenumber_field.phonenumber import PhoneNumber
        tm = TestModelBlankPhone()
        tm.save()
        
        pk = tm.id
        tm = TestModelBlankPhone.objects.get(pk=pk)
        self.assertIsNone(tm.phone)
