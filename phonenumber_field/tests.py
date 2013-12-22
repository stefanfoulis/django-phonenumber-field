#-*- coding: utf-8 -*-
from django.test.testcases import TestCase
from django.db import models

from phonenumber_field.modelfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber


###############
# Test Models #
###############

class MandatoryPhoneNumber(models.Model):
    phone_number = PhoneNumberField()


class OptionalPhoneNumber(models.Model):
    phone_number = PhoneNumberField(blank=True, default='')


##############
# Test Cases #
##############


class PhoneNumberFieldTestCase(TestCase):
    test_number_1 = '+414204242'
    test_number_ext = 'tel:+1-800-765-4321;ext=111'
    equal_number_strings = ['+44 113 8921113', '+441138921113']
    local_numbers = [
        ('GB', '01606 751 78'),
        ('DE', '0176/96842671'),
    ]
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
        self.assertTrue(all(n==numbers[0] for n in numbers))
    
    def test_same_number_different_extensions_not_equal(self):
        p1 = OptionalPhoneNumber()
        p1.phone_number = self.test_number_ext
        p2 = OptionalPhoneNumber()
        p2.phone_number = p1.phone_number.as_e164
        p3 = OptionalPhoneNumber()
        p3.phone_number = "%sx%s9" % (p2.phone_number.as_e164, p1.phone_number.extension)
        self.assertEqual(p2.phone_number.extension, None)
        self.assertNotEqual(p1.phone_number.extension, p3.phone_number.extension)
        self.assertNotEqual(p1.phone_number.extension, p2.phone_number.extension)
        self.assertNotEqual(p1.phone_number, p2.phone_number)
        self.assertNotEqual(p1.phone_number, p3.phone_number)

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
    
    def test_can_hash_for_m2m(self):
        p1 = OptionalPhoneNumber()
        p1.phone_number = self.test_number_1
        p1h = hash(p1.phone_number)
        p2 = OptionalPhoneNumber()
        p2.phone_number = self.equal_number_strings[0]
        p2h = hash(p2.phone_number)
        p3 = OptionalPhoneNumber()
        p3.phone_number = self.equal_number_strings[1]
        p3h = hash(p3.phone_number)
        self.assertNotEqual(p1h, p2h)
        self.assertEqual(p2h,p3h)
    
    def test_extensions_survive_database(self):
        p1 = MandatoryPhoneNumber()
        p1.phone_number = self.test_number_ext
        
        self.assertTrue(p1.phone_number.is_valid())
        self.assertTrue(p1.phone_number.extension)
        
        db_val = PhoneNumberField().get_prep_value(p1.phone_number)
        p2 = MandatoryPhoneNumber()
        p2.phone_number = db_val
        
        self.assertTrue(p2.phone_number.is_valid())
        self.assertEqual(p1.phone_number.extension, p2.phone_number.extension)
        self.assertEqual(p1.phone_number, p2.phone_number)