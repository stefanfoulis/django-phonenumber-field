from unittest import mock

from django import forms
from django.test import SimpleTestCase, override_settings
from django.utils.functional import lazy

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

    @override_settings(PHONENUMBER_DEFAULT_REGION="FR")
    def test_error_message_uses_default_region(self):
        class PhoneNumberForm(forms.Form):
            number = PhoneNumberField()

        form = PhoneNumberForm({"number": "invalid"})
        self.assertIs(form.is_valid(), False)
        self.assertEqual(
            form.errors,
            {
                "number": [
                    "Enter a valid phone number (e.g. 01 23 45 67 89) "
                    "or a number with an international call prefix."
                ]
            },
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

    def test_error_message_lazy(self):
        def fail_gettext(msgid):
            raise Exception("gettext was called unexpectedly.")

        with mock.patch(
            "phonenumber_field.formfields._",
            side_effect=lazy(fail_gettext, str),
        ):
            PhoneNumberField()
