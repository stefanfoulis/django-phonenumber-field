from unittest import mock

import django
from django import forms
from django.test import SimpleTestCase, override_settings
from django.utils.functional import lazy

from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget

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

    @override_settings(PHONENUMBER_DEFAULT_REGION="FR")
    def test_input_not_cleared_on_other_field_error(self):
        class PhoneNumberForm(forms.Form):
            name = forms.CharField(min_length=4, max_length=100)
            number = PhoneNumberField(required=False, widget=PhoneNumberPrefixWidget())

        form = PhoneNumberForm({"name": "a", "number_0": "FR", "number_1": "612345678"})
        self.assertIs(form.is_valid(), False)
        self.assertEqual(
            form.errors,
            {"name": ["Ensure this value has at least 4 characters (it has 1)."]},
        )
        self.maxDiff = None
        form_html = form.as_p()
        aria_invalid = "" if django.VERSION[0] < 5 else 'aria-invalid="true" '
        self.assertInHTML(
            f"""
            <ul class="errorlist">
                <li>
                Ensure this value has at least 4 characters (it has 1).
                </li>
            </ul>
            <p>
                <label for="id_name">Name:</label>
                <input
                   id="id_name"
                   maxlength="100"
                   minlength="4"
                   name="name"
                   {aria_invalid}
                   required
                   type="text"
                   value="a">
            </p>
            """,
            form_html,
            count=1,
        )
        self.assertInHTML(
            '<option selected value="FR">France +33</option>',
            form_html,
            count=1,
        )
        self.assertInHTML(
            '<input id="id_number_1" name="number_1" type="text" value="612345678">',
            form_html,
            count=1,
        )

    def test_override_widget(self):
        class MyPhoneNumberField(PhoneNumberField):
            widget = forms.TextInput

        class TestForm(forms.Form):
            phone = MyPhoneNumberField(region="FR")

        form = TestForm({"phone": "+33612345678"})
        self.assertIs(form.is_valid(), True)
        self.assertHTMLEqual(
            form.as_p(),
            """
            <p>
            <label for="id_phone">Phone:</label>
            <input id="id_phone" name="phone" required type="tel" value="+33612345678">
            </p>
            """,
        )

    @override_settings(PHONENUMBER_DEFAULT_REGION="FR")
    def test_widget_uses_default_region(self):
        class TestForm(forms.Form):
            phone = PhoneNumberField()

        form = TestForm({"phone": "+33612345678"})
        self.assertIs(form.is_valid(), True)
        self.assertHTMLEqual(
            form.as_p(),
            """
            <p>
            <label for="id_phone">Phone:</label>
            <input
               id="id_phone"
               name="phone"
               required
               type="tel"
               value="06 12 34 56 78">
            </p>
            """,
        )
