"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError, DEFAULT_DB_ALIAS
from django.test import TestCase
from unittest import skipIf

DATABASE_IS_SQLITE = settings.DATABASES[DEFAULT_DB_ALIAS]['ENGINE'] == 'django.db.backends.sqlite3'

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

class CICharFieldTestModelTestCase(TestCase):
    def test_integrity_error(self):
        from testapp.models import CICharFieldTestModel
        self.assertEqual(CICharFieldTestModel.objects.count(), 0)
        
        CICharFieldTestModel.objects.create(value="a")
        self.assertEqual(CICharFieldTestModel.objects.count(), 1)
        
        with self.assertRaises(IntegrityError):
            CICharFieldTestModel.objects.create(value="A")
    
    def test_max_length(self):
        from testapp.models import CICharFieldTestModel
        obj = CICharFieldTestModel(value="bb")
        with self.assertRaises(ValidationError):
            obj.full_clean()
    
    @skipIf(DATABASE_IS_SQLITE, "Sqlite does not enforce varchar max_length")
    def test_max_length_db(self):
        from testapp.models import CICharFieldTestModel
        self.assertEqual(CICharFieldTestModel.objects.count(), 0)
        
        CICharFieldTestModel.objects.create(value="bb")
        self.assertNotEqual(CICharFieldTestModel.objects.all()[0].value.lower(), "bb")
    
    @skipIf(DATABASE_IS_SQLITE, "Sqlite does not enforce varchar max_length")
    def test_max_length_db_truncates(self):
        from testapp.models import CICharFieldTestModel
        self.assertEqual(CICharFieldTestModel.objects.count(), 0)
        
        CICharFieldTestModel.objects.create(value="bb")
        self.assertEqual(CICharFieldTestModel.objects.all()[0].value.lower(), "b")
    
    def test_lookup(self):
        from testapp.models import CICharFieldTestModel
        self.assertEqual(CICharFieldTestModel.objects.count(), 0)
        
        a_lower = "a"
        a_upper = "A"
        
        CICharFieldTestModel.objects.create(value=a_lower)
        self.assertEqual(CICharFieldTestModel.objects.count(), 1)
        
        a = CICharFieldTestModel.objects.get(value=a_upper)
        self.assertEqual(a.value.upper(), a_upper)
        
        a.delete()
        
        self.assertEqual(CICharFieldTestModel.objects.count(), 0)
        
        CICharFieldTestModel.objects.create(value=a_upper)
        self.assertEqual(CICharFieldTestModel.objects.count(), 1)
        
        A = CICharFieldTestModel.objects.get(value=a_lower)
        self.assertEqual(A.value.lower(), a_lower)
