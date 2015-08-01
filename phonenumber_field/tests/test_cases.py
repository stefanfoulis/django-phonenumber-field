# -*- coding: utf-8 -*-
import phonenumbers

from django.test.testcases import TestCase
from django.db import models

from phonenumbers import is_number_match, MatchType
from phonenumbers.data import _AVAILABLE_REGION_CODES

from phonenumber_field.modelfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber
from phonenumber_field.validators import to_python
from phonenumber_field.widgets import CountryCodeSelect
from django.conf import settings
from unittest import skipIf
from django.core.exceptions import ValidationError
from django.db import IntegrityError, DEFAULT_DB_ALIAS

from .models import *

DATABASE_IS_SQLITE = settings.DATABASES[DEFAULT_DB_ALIAS]['ENGINE'] == 'django.db.backends.sqlite3'

##############
# Test Cases #
##############


class PhoneNumberFieldTestCase(TestCase):
    test_number_1 = '+414204242'
    equal_number_strings = ['+44 113 8921113', '+441138921113']
    local_numbers = [
        ('GB', '01606 751 78'),
        ('DE', '0176/96842671'),
    ]
    storage_numbers = {
        'E164': ['+44 113 8921113', '+441138921113'],
        'RFC3966': ['+44 113 8921113', 'tel:+44-113-892-1113'],
        'INTERNATIONAL': ['+44 113 8921113', '+44 113 892 1113'],
    }
    invalid_numbers = ['+44 113 892111', ]

    def test_valid_numbers_are_valid(self):
        numbers = [PhoneNumber.from_string(number_string)
                   for number_string in self.equal_number_strings]
        self.assertTrue(all([number.is_valid() for number in numbers]))
        numbers = [PhoneNumber.from_string(number_string, region=region)
                   for region, number_string in self.local_numbers]
        self.assertTrue(all([number.is_valid() for number in numbers]))

    def test_invalid_numbers_are_invalid(self):
        numbers = [PhoneNumber.from_string(number_string)
                   for number_string in self.invalid_numbers]
        self.assertTrue(all([not number.is_valid() for number in numbers]))

    def test_objects_with_same_number_are_equal(self):
        numbers = [
            MandatoryPhoneNumber.objects.create(
                phone_number=number_string).phone_number
            for number_string in self.equal_number_strings]
        self.assertTrue(all(is_number_match(n, numbers[0]) == MatchType.EXACT_MATCH
                        for n in numbers))

    def test_field_returns_correct_type(self):
        model = OptionalPhoneNumber()
        self.assertEqual(model.phone_number, None)
        model.phone_number = '+49 176 96842671'
        self.assertEqual(type(model.phone_number), PhoneNumber)

    def test_can_assign_string_phone_number(self):
        opt_phone = OptionalPhoneNumber()
        opt_phone.phone_number = self.test_number_1
        self.assertEqual(type(opt_phone.phone_number), PhoneNumber)
        self.assertEqual(opt_phone.phone_number.as_e164, self.test_number_1)

    def test_does_not_fail_on_invalid_values(self):
        # testcase for
        # https://github.com/stefanfoulis/django-phonenumber-field/issues/11
        phone = to_python(42)
        self.assertEqual(phone, None)

    def _test_storage_formats(self):
        '''
        Aggregate of tests to perform for db storage formats
        '''
        self.test_objects_with_same_number_are_equal()
        self.test_field_returns_correct_type()
        self.test_can_assign_string_phone_number()

    def test_storage_formats(self):
        '''
        Perform aggregate tests for all db storage formats
        '''
        old_format = getattr(settings, 'PHONENUMBER_DB_FORMAT', 'E164')
        for frmt in PhoneNumber.format_map:
            setattr(settings, 'PHONENUMBER_DB_FORMAT', frmt)
            self._test_storage_formats()
        setattr(settings, 'PHONENUMBER_DB_FORMAT', old_format)

    def test_prep_value(self):
        '''
        Tests correct db storage value against different setting of
        PHONENUMBER_DB_FORMAT
        Required output format is set as string constant to guarantee
        consistent database storage values
        '''
        number = PhoneNumberField()
        old_format = getattr(settings, 'PHONENUMBER_DB_FORMAT', 'E164')
        for frmt in ['E164', 'RFC3966', 'INTERNATIONAL']:
            setattr(settings, 'PHONENUMBER_DB_FORMAT', frmt)
            self.assertEqual(
                number.get_prep_value(
                    to_python(self.storage_numbers[frmt][0])
                ),
                self.storage_numbers[frmt][1])
        setattr(settings, 'PHONENUMBER_DB_FORMAT', old_format)


class PhoneNumberObjectTestCase(TestCase):
    def test_attrs_are_not_masking(self):
        pn = phonenumbers.phonenumber.PhoneNumber()
        
        self.assertFalse(hasattr(pn, "_region_code"))
        self.assertFalse(hasattr(pn, "region_code"))
        self.assertFalse(hasattr(pn, "region_code_sep"))
        self.assertFalse(hasattr(pn, "format_map"))
    
    def test_region_code_property(self):
        pn = PhoneNumber()
        
        for rc in _AVAILABLE_REGION_CODES:
            self.assertEqual(rc, rc.upper(), "It is assumed that region codes are all upper case.")
            self.assertEqual(len(rc), 2, "It is assumed that region codes are all of length 2")
        
        valid_region_code = _AVAILABLE_REGION_CODES[0]
        lower_case_valid_region_code = valid_region_code.lower()
        
        invalid_region_code = "9z"
        self.assertNotIn(invalid_region_code, _AVAILABLE_REGION_CODES)
        
        with self.assertRaises(ValueError):
            pn.region_code = invalid_region_code
        
        with self.assertRaises(TypeError):
            pn.region_code = 1
        
        pn.region_code = valid_region_code
        self.assertEqual(pn.region_code, valid_region_code)
        
        pn.region_code = None
        self.assertIsNone(pn.region_code)
        
        pn.region_code = lower_case_valid_region_code
        self.assertEqual(pn.region_code, valid_region_code)

class CountryCodeSelectWidgetTestCase(TestCase):
    def test_choices_update_with_database(self):
        widget = CountryCodeSelect()
        
        choice = list(widget.choices)[-1][0]
        
        self.assertTrue(choice[0])# verify we didn't get the empty choice
        
        country_code = widget.country_code_from_choice(choice)
        country_code.active = False
        country_code.save()
        
        self.assertNotIn(choice[0], [c[0] for c in widget.choices])

class CICharFieldTestModelTestCase(TestCase):
    def test_integrity_error(self):
        self.assertEqual(CICharFieldTestModel.objects.count(), 0)
        
        CICharFieldTestModel.objects.create(value="a")
        self.assertEqual(CICharFieldTestModel.objects.count(), 1)
        
        with self.assertRaises(IntegrityError):
            CICharFieldTestModel.objects.create(value="A")
    
    def test_max_length(self):
        obj = CICharFieldTestModel(value="bb")
        with self.assertRaises(ValidationError):
            obj.full_clean()
    
    @skipIf(DATABASE_IS_SQLITE, "Sqlite does not enforce varchar max_length")
    def test_max_length_db(self):
        self.assertEqual(CICharFieldTestModel.objects.count(), 0)
        
        CICharFieldTestModel.objects.create(value="bb")
        self.assertNotEqual(CICharFieldTestModel.objects.all()[0].value.lower(), "bb")
    
    @skipIf(DATABASE_IS_SQLITE, "Sqlite does not enforce varchar max_length")
    def test_max_length_db_truncates(self):
        self.assertEqual(CICharFieldTestModel.objects.count(), 0)
        
        CICharFieldTestModel.objects.create(value="bb")
        self.assertEqual(CICharFieldTestModel.objects.all()[0].value.lower(), "b")
    
    def test_lookup(self):
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
