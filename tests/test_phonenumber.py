import phonenumbers
from django.test import SimpleTestCase, override_settings

from phonenumber_field.phonenumber import PhoneNumber


class PhoneNumberTest(SimpleTestCase):
    def test_phonenumber_default_format(self):
        phone = PhoneNumber.from_string("+33612345678")
        # E164 by default.
        self.assertEqual(str(phone), "+33612345678")
        with override_settings(PHONENUMBER_DEFAULT_FORMAT="E164"):
            self.assertEqual(str(phone), "+33612345678")
        with override_settings(PHONENUMBER_DEFAULT_FORMAT="INTERNATIONAL"):
            self.assertEqual(str(phone), "+33 6 12 34 56 78")
        with override_settings(PHONENUMBER_DEFAULT_FORMAT="NATIONAL"):
            self.assertEqual(str(phone), "06 12 34 56 78")
        with override_settings(PHONENUMBER_DEFAULT_FORMAT="RFC3966"):
            self.assertEqual(str(phone), "tel:+33-6-12-34-56-78")


class PhoneNumberOrdering(SimpleTestCase):
    def test_ordering(self):
        phone1 = PhoneNumber.from_string("+33600000000")
        phone2 = PhoneNumber.from_string("+33600000001")
        self.assertLess(phone1, phone2)
        # Ordering is total.
        self.assertGreater(phone2, phone1)
        self.assertLessEqual(phone1, phone1)
        self.assertGreaterEqual(phone1, phone1)
        self.assertEqual(phone1, phone1)

    def test_ordering_with_phonenumbers(self):
        phone1 = PhoneNumber.from_string("+33600000000")
        phone2 = phonenumbers.parse("+33600000001")
        self.assertLess(phone1, phone2)

    def test_ordering_contains_None(self):
        phone1 = PhoneNumber.from_string("+33600000000")
        msg = "'<' not supported between instances of 'PhoneNumber' and 'NoneType'"
        for assertion in [
            self.assertLess,
            self.assertLessEqual,
            self.assertGreater,
            self.assertGreaterEqual,
        ]:
            with self.subTest(assertion):
                with self.assertRaisesMessage(TypeError, msg):
                    assertion(phone1, None)

    def test_ordering_with_invalid_value(self):
        phone1 = PhoneNumber.from_string("+33600000000")
        invalid = PhoneNumber.from_string("+1000000000")
        invalid_phonenumbers = phonenumbers.parse("+1000000000")
        for number in [invalid, invalid_phonenumbers]:
            with self.subTest(number):
                for p1, p2 in [[phone1, number], [number, phone1]]:
                    with self.subTest([p1, p2]):
                        with self.assertRaisesRegex(
                            ValueError, r"^Invalid phone number: "
                        ):
                            self.assertLess(p1, p2)
