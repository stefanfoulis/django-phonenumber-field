from django import forms
from django.test import SimpleTestCase

from phonenumber_field.formfields import PhoneNumberField

ALGERIAN_PHONE_NUMBER = "+213799136332"


class PhoneNumberFormFieldTest(SimpleTestCase):
    def test_error_message(self):
        class PhoneNumberForm(forms.Form):
            number = PhoneNumberField()

        form = PhoneNumberForm({"number": "invalid"})
        self.assertIs(form.is_valid(), False)
        self.assertEqual(
            form.errors, {"number": ["Enter a valid phone number (e.g. +12125552368)."]}
        )

    def test_override_error_message(self):
        class MyPhoneNumberField(PhoneNumberField):
            default_error_messages = {"invalid": "MY INVALID MESSAGE!"}

        class PhoneNumberForm(forms.Form):
            number = MyPhoneNumberField()

        form = PhoneNumberForm({"number": "invalid"})
        self.assertIs(form.is_valid(), False)
        self.assertEqual(form.errors, {"number": ["MY INVALID MESSAGE!"]})

    def test_override_error_message_inline(self):
        class PhoneNumberForm(forms.Form):
            number = PhoneNumberField(
                error_messages={"invalid": "MY INLINE INVALID MESSAGE!"}
            )

        form = PhoneNumberForm({"number": "invalid"})
        self.assertIs(form.is_valid(), False)
        self.assertEqual(form.errors, {"number": ["MY INLINE INVALID MESSAGE!"]})

    def test_algerian_phone_number_in_form(self):
        class PhoneNumberForm(forms.Form):
            number = PhoneNumberField()

        form = PhoneNumberForm({"number": ALGERIAN_PHONE_NUMBER})
        self.assertTrue(form.is_valid())
        self.assertEqual(ALGERIAN_PHONE_NUMBER, form.cleaned_data["number"])
