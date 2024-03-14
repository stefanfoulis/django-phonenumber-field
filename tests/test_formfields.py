from unittest import mock

import django
import phonenumbers
from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, override_settings
from django.utils import translation
from django.utils.functional import lazy

from phonenumber_field.formfields import PhoneNumberField, SplitPhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber
from phonenumber_field.validators import validate_phonenumber

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

    def test_invalid_phone_number(self):
        class PhoneNumberForm(forms.Form):
            number = PhoneNumberField()

        form = PhoneNumberForm({"number": "+11234567890"})
        self.assertIs(form.is_valid(), False)
        self.assertEqual(
            form.errors, {"number": ["Enter a valid phone number (e.g. +12125552368)."]}
        )

    def test_validate_shortcode(self):
        class ShortCodePhoneNumberField(PhoneNumberField):
            default_validators = [validate_phonenumber]

        class TestForm(forms.Form):
            phone = ShortCodePhoneNumberField(region="FR")

        form = TestForm({"phone": "1010"})
        self.assertIs(form.is_valid(), True)


class SplitPhoneNumberFormFieldTest(SimpleTestCase):
    def example_number(self, region_code: str) -> PhoneNumber:
        number = phonenumbers.example_number(region_code)
        assert number is not None
        e164 = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
        return PhoneNumber.from_string(e164, region=region_code)

    def test_initial_empty(self):
        class TestForm(forms.Form):
            phone = SplitPhoneNumberField(region="CN")

        rendered = str(TestForm())
        self.assertIn('<option value="">---------</option>', rendered)
        self.assertIn('<option value="CN" selected>China +86</option>', rendered)

    @override_settings(PHONENUMBER_DEFAULT_REGION="CN")
    def test_uses_default_region_as_initial(self):
        class TestForm(forms.Form):
            phone = SplitPhoneNumberField()

        rendered = str(TestForm())
        self.assertIn('<option value="">---------</option>', rendered)
        self.assertIn('<option value="CN" selected>China +86</option>', rendered)

    def test_no_initial(self):
        class TestForm(forms.Form):
            phone = SplitPhoneNumberField()

        rendered = str(TestForm())
        self.assertIn('<option value="" selected>---------</option>', rendered)
        self.assertIn('<option value="CN">China +86</option>', rendered)

    def test_initial(self):
        class TestForm(forms.Form):
            phone = SplitPhoneNumberField()

        rendered = str(
            TestForm(initial={"phone": PhoneNumber.from_string("+33612345678")})
        )
        self.assertIn('<option value="">---------</option>', rendered)
        self.assertIn('<option value="FR" selected>France +33</option>', rendered)
        self.assertIn(
            '<input type="tel" name="phone_1" value="612345678" '
            'required id="id_phone_1">',
            rendered,
        )

    def test_invalid_phone_number(self):
        class TestForm(forms.Form):
            phone = SplitPhoneNumberField()

        form = TestForm({"phone_0": "US", "phone_1": "1234567890"})
        self.assertIs(form.is_valid(), False)
        self.assertEqual(
            form.errors,
            {"phone": ["Enter a valid phone number (e.g. (201) 555-0123)."]},
        )

    @override_settings(USE_I18N=True)
    def test_after_translation_deactivate_all(self):
        class TestForm(forms.Form):
            phone = SplitPhoneNumberField()

        translation.deactivate_all()
        rendered = str(TestForm())
        self.assertIn(
            '<select name="phone_0" required id="id_phone_0">'
            '<option value="" selected>---------</option>',
            rendered,
        )

    def test_example_numbers(self):
        example_numbers = (
            self.example_number("US"),
            self.example_number("CA"),
            self.example_number("GB"),
            self.example_number("GG"),
            self.example_number("PL"),
            self.example_number("IT"),
        )
        tests = [
            (
                {
                    "phone_0": phonenumbers.region_code_for_number(number),
                    "phone_1": phonenumbers.national_significant_number(number),
                },
                number,
            )
            for number in example_numbers
        ]

        class TestForm(forms.Form):
            phone = SplitPhoneNumberField()

        for data, expected in tests:
            with self.subTest(data):
                form = TestForm(data=data)
                self.assertIs(form.is_valid(), True)
                self.assertEqual(form.cleaned_data, {"phone": expected})

    def test_empty_region(self):
        class TestForm(forms.Form):
            phone = SplitPhoneNumberField()

        invalid_national_number = "8876543210"
        form = TestForm(data={"phone_0": "", "phone_1": invalid_national_number})
        self.assertFalse(form.is_valid())
        rendered_form = form.as_ul()
        self.assertInHTML(
            '<ul class="errorlist"><li>This field is required.</li></ul>',
            rendered_form,
        )
        aria_invalid = "" if django.VERSION[0] < 5 else 'aria-invalid="true" '
        # Keeps national number input.
        self.assertInHTML(
            '<input type="tel" name="phone_1" '
            f'value="{invalid_national_number}" {aria_invalid} required '
            'id="id_phone_1">',
            rendered_form,
            count=1,
        )
        self.assertInHTML(
            '<option value="" selected>---------</option>',
            rendered_form,
            count=1,
        )

    def test_empty_national_number(self):
        class TestForm(forms.Form):
            phone = SplitPhoneNumberField()

        form = TestForm(data={"phone_0": "CA", "phone_1": ""})
        self.assertFalse(form.is_valid())
        rendered_form = form.as_ul()
        self.assertInHTML(
            '<ul class="errorlist"><li>This field is required.</li></ul>',
            rendered_form,
        )
        aria_invalid = "" if django.VERSION[0] < 5 else 'aria-invalid="true" '
        self.assertInHTML(
            f'<input type="tel" name="phone_1" {aria_invalid} '
            'required id="id_phone_1">',
            rendered_form,
            count=1,
        )

    def test_not_required_empty_data(self):
        class TestForm(forms.Form):
            phone = SplitPhoneNumberField(required=False)

        form = TestForm(data={"phone_0": "", "phone_1": ""})
        self.assertIs(form.is_valid(), True)

    def test_no_region(self):
        class TestForm(forms.Form):
            phone = SplitPhoneNumberField()

        form = TestForm(data={"phone_1": "654321"})
        self.assertFalse(form.is_valid())
        rendered_form = form.as_ul()
        self.assertInHTML(
            '<ul class="errorlist"><li>This field is required.</li></ul>',
            rendered_form,
        )
        aria_invalid = "" if django.VERSION[0] < 5 else 'aria-invalid="true" '
        self.assertInHTML(
            f'<input type="tel" name="phone_1" value="654321" {aria_invalid} '
            'required id="id_phone_1">',
            rendered_form,
            count=1,
        )
        self.assertInHTML(
            '<option value="" selected>---------</option>',
            rendered_form,
            count=1,
        )

    def test_no_national_number(self):
        class TestForm(forms.Form):
            phone = SplitPhoneNumberField()

        form = TestForm(data={"phone_0": "CA"})
        self.assertFalse(form.is_valid())
        rendered_form = form.as_ul()
        self.assertInHTML(
            '<ul class="errorlist"><li>This field is required.</li></ul>',
            rendered_form,
            count=1,
        )
        aria_invalid = "" if django.VERSION[0] < 5 else 'aria-invalid="true" '
        self.assertInHTML(
            f'<input type="tel" name="phone_1" {aria_invalid} '
            'required id="id_phone_1">',
            rendered_form,
            count=1,
        )

    def test_not_required_no_data(self):
        class TestForm(forms.Form):
            phone = SplitPhoneNumberField(required=False)

        form = TestForm(data={})
        self.assertIs(form.is_valid(), True)

    def test_keeps_region_with_invalid_national_number(self):
        class TestForm(forms.Form):
            phone = SplitPhoneNumberField()

        form = TestForm(data={"phone_0": "CA", "phone_1": "0000"})
        self.assertFalse(form.is_valid())
        rendered_form = str(form)
        self.assertInHTML(
            '<ul class="errorlist">'
            "<li>Enter a valid phone number (e.g. (506) 234-5678).</li></ul>",
            rendered_form,
        )
        aria_invalid = "" if django.VERSION[0] < 5 else 'aria-invalid="true" '
        self.assertInHTML(
            f'<input type="tel" name="phone_1" value="0000" {aria_invalid} '
            'required id="id_phone_1">',
            rendered_form,
            count=1,
        )
        self.assertInHTML(
            '<option value="CA" selected>Canada +1</option>',
            rendered_form,
            count=1,
        )

    def test_maxlength_not_in_select(self):
        # Regression test for #490
        class TestForm(forms.Form):
            phone = SplitPhoneNumberField()

        rendered = str(TestForm())
        self.assertIn('<select name="phone_0" required id="id_phone_0">', rendered)

    def test_custom_attrs(self):
        class SplitPhoneNumberFieldWithClass(SplitPhoneNumberField):
            def prefix_field(self):
                prefix_field = super().prefix_field()
                prefix_field.widget.attrs["class"] = "prefix-input"
                return prefix_field

            def number_field(self):
                number_field = super().number_field()
                number_field.widget.attrs["class"] = "number-input"
                return number_field

        class TestForm(forms.Form):
            phone = SplitPhoneNumberFieldWithClass()

        rendered = str(TestForm())
        self.assertIn(
            '<select name="phone_0" class="prefix-input" required id="id_phone_0">',
            rendered,
        )
        self.assertInHTML(
            '<input type="tel" name="phone_1" class="number-input"'
            'required id="id_phone_1">',
            rendered,
            count=1,
        )

    def test_custom_choices(self):
        class SplitPhoneNumberFieldWithCountries(SplitPhoneNumberField):
            def prefix_field(self):
                return forms.ChoiceField(choices=[("FR", "France"), ("BE", "Belgium")])

        class TestForm(forms.Form):
            phone = SplitPhoneNumberFieldWithCountries()

        form = TestForm()
        if django.VERSION[0] < 4:
            self.assertHTMLEqual(
                str(form.as_p()),
                """
                <p>
                <label for="id_phone_0">Phone:</label>
                <select id="id_phone_0" name="phone_0" required>
                    <option value="FR">France</option>
                    <option value="BE">Belgium</option>
                </select>
                <input id="id_phone_1" name="phone_1" required type="tel">
                </p>
                """,
            )
        else:
            self.assertHTMLEqual(
                form.as_div(),
                """
                <div>
                <fieldset>
                <legend>
                Phone:
                </legend>
                <select id="id_phone_0" name="phone_0" required>
                    <option value="FR">France</option>
                    <option value="BE">Belgium</option>
                </select>
                <input id="id_phone_1" name="phone_1" required type="tel">
                </fieldset>
                </div>
                """,
            )

    def test_invalid_region(self):
        class PhoneNumberForm(forms.Form):
            number = SplitPhoneNumberField()

        form = PhoneNumberForm({"number_0": "NONEXISTENT", "number_1": "+33612345678"})
        self.assertIs(form.is_valid(), False)
        self.assertEqual(
            form.errors,
            {
                "number": [
                    "Select a valid choice. "
                    "NONEXISTENT is not one of the available choices."
                ]
            },
        )

    @override_settings(PHONENUMBER_DEFAULT_REGION="FR")
    def test_input_not_cleared_on_other_field_error(self):
        class PhoneNumberForm(forms.Form):
            name = forms.CharField(min_length=4, max_length=100)
            number = SplitPhoneNumberField(required=False)

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
            '<input id="id_number_1" name="number_1" type="tel" value="612345678">',
            form_html,
            count=1,
        )

    def test_without_babel(self):
        import phonenumber_field.formfields

        babel = phonenumber_field.formfields.babel

        def restore_babel():
            phonenumber_field.formfields.babel = babel

        self.addCleanup(restore_babel)
        phonenumber_field.formfields.babel = None
        with self.assertRaises(ImproperlyConfigured):
            SplitPhoneNumberField()

    def test_error_message_is_localized(self):
        class PhoneNumberForm(forms.Form):
            number = SplitPhoneNumberField()

        form = PhoneNumberForm({"number_0": "FR", "number_1": "1"})
        self.assertIn(
            '<ul class="errorlist"><li>'
            "Enter a valid phone number (e.g. 01 23 45 67 89)."
            "</li></ul>",
            str(form),
        )

    def test_customize_invalid_error_message(self):
        class CustomSplitPhoneNumberField(SplitPhoneNumberField):
            def invalid_error_message(self):
                return "My message using {example_number}."

        class TestForm(forms.Form):
            phone = CustomSplitPhoneNumberField()

        form = TestForm({"phone_0": "FR", "phone_1": "1"})
        self.assertIn(
            '<ul class="errorlist"><li>'
            "My message using 01 23 45 67 89."
            "</li></ul>",
            str(form),
        )

    def test_clean_handles_invalid_input(self):
        data = [
            # require_all_fields, phone_data, error_message
            (True, {"phone_0": "", "phone_1": "1234"}, "This field is required."),
            (True, {}, "This field is required."),
            (True, {"phone_1": "1234"}, "This field is required."),
            (
                True,
                {"phone_0": "invalid", "phone_1": "1234"},
                "Select a valid choice. invalid is not one of the available choices.",
            ),
            (False, {"phone_0": "", "phone_1": "1234"}, "Enter a complete value."),
            (False, {}, "This field is required."),
            (False, {"phone_1": "1234"}, "Enter a complete value."),
            (
                False,
                {"phone_0": "invalid", "phone_1": "1234"},
                "Select a valid choice. invalid is not one of the available choices.",
            ),
        ]
        for all_fields_required, phone_data, error_message in data:
            with self.subTest(
                f"require_all_fields={all_fields_required},"
                f"{phone_data=},"
                f"{error_message=}"
            ):

                class TestForm(forms.Form):
                    phone = SplitPhoneNumberField(
                        require_all_fields=all_fields_required
                    )

                form = TestForm(phone_data)
                self.assertIs(form.is_valid(), False)
                self.assertEqual(form.errors["phone"], [error_message])

    def test_validate_shortcode(self):
        class ShortCodeSplitPhoneNumberField(SplitPhoneNumberField):
            default_validators = [validate_phonenumber]

        class TestForm(forms.Form):
            phone = ShortCodeSplitPhoneNumberField()

        form = TestForm({"phone_0": "FR", "phone_1": "1010"})
        self.assertIs(form.is_valid(), True)
