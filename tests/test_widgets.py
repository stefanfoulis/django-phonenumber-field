import phonenumbers
from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, override_settings
from django.utils import translation

from phonenumber_field import formfields, widgets
from phonenumber_field.phonenumber import PhoneNumber
from phonenumber_field.widgets import (
    PhoneNumberInternationalFallbackWidget,
    PhoneNumberPrefixWidget,
)


class PhonePrefixSelectTest(SimpleTestCase):
    def setUp(self):
        super().setUp()
        self.babel_module = widgets.babel

    def test_without_babel(self):
        widgets.babel = None
        with self.assertRaises(ImproperlyConfigured):
            widgets.PhonePrefixSelect()

    def tearDown(self):
        widgets.babel = self.babel_module
        super().tearDown()


def example_number(region_code: str) -> PhoneNumber:
    number = phonenumbers.example_number(region_code)
    e164 = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
    return PhoneNumber.from_string(e164, region=region_code)


EXAMPLE_NUMBERS = (
    example_number("US"),
    example_number("CA"),
    example_number("GB"),
    example_number("GG"),
    example_number("PL"),
    example_number("IT"),
)


class PhoneNumberPrefixWidgetTest(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        class TestForm(forms.Form):
            phone = formfields.PhoneNumberField(widget=PhoneNumberPrefixWidget)

        cls.form_class = TestForm

    def test_initial(self):
        rendered = PhoneNumberPrefixWidget(initial="CN").render("", "")
        self.assertIn('<option value="">---------</option>', rendered)
        self.assertIn('<option value="CN" selected>China +86</option>', rendered)

    @override_settings(PHONENUMBER_DEFAULT_REGION="CN")
    def test_uses_default_region_as_initial(self):
        rendered = PhoneNumberPrefixWidget().render("", "")
        self.assertIn('<option value="">---------</option>', rendered)
        self.assertIn('<option value="CN" selected>China +86</option>', rendered)

    def test_no_initial(self):
        rendered = PhoneNumberPrefixWidget().render("", "")
        self.assertIn('<option value="" selected>---------</option>', rendered)
        self.assertIn('<option value="CN">China +86</option>', rendered)

    @override_settings(USE_I18N=True)
    def test_after_translation_deactivate_all(self):
        translation.deactivate_all()
        rendered = PhoneNumberPrefixWidget().render("", "")
        self.assertIn(
            '<select name="_0"><option value="" selected>---------</option>', rendered
        )

    def test_value_from_datadict(self):
        tests = [
            (
                {
                    "phone_0": phonenumbers.region_code_for_number(number),
                    "phone_1": phonenumbers.national_significant_number(number),
                },
                number,
            )
            for number in EXAMPLE_NUMBERS
        ]

        for data, expected in tests:
            with self.subTest(data):
                form = self.form_class(data=data)
                self.assertIs(form.is_valid(), True)
                self.assertEqual(form.cleaned_data, {"phone": expected})

    def test_empty_region(self):
        invalid_national_number = "8876543210"
        form = self.form_class(data={"phone_0": "", "phone_1": invalid_national_number})
        self.assertFalse(form.is_valid())
        rendered_form = form.as_ul()
        self.assertInHTML(
            '<ul class="errorlist"><li>Enter a valid phone number '
            "(e.g. +12125552368).</li></ul>",
            rendered_form,
        )
        # Keeps national number input.
        self.assertInHTML(
            f'<input type="text" name="phone_1" '
            f'value="{invalid_national_number}" required id="id_phone_1">',
            rendered_form,
            count=1,
        )
        self.assertInHTML(
            '<option value="" selected>---------</option>',
            rendered_form,
            count=1,
        )

    def test_empty_national_number(self):
        form = self.form_class(data={"phone_0": "CA", "phone_1": ""})
        self.assertFalse(form.is_valid())
        rendered_form = form.as_ul()
        self.assertInHTML(
            '<ul class="errorlist"><li>The phone number entered is not valid.'
            "</li></ul>",
            rendered_form,
        )
        self.assertInHTML(
            '<input type="text" name="phone_1" required id="id_phone_1">',
            rendered_form,
            count=1,
        )
        self.assertInHTML(
            '<option value="CA" selected>Canada +1</option>',
            rendered_form,
            count=1,
        )

    def test_no_region(self):
        form = self.form_class(data={"phone_1": "654321"})
        self.assertFalse(form.is_valid())
        rendered_form = form.as_ul()
        self.assertInHTML(
            '<ul class="errorlist"><li>Enter a valid phone number '
            "(e.g. +12125552368).</li></ul>",
            rendered_form,
        )
        self.assertInHTML(
            '<input type="text" name="phone_1" value="654321" '
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
        form = self.form_class(data={"phone_0": "CA"})
        self.assertFalse(form.is_valid())
        rendered_form = form.as_ul()
        self.assertInHTML(
            '<ul class="errorlist"><li>The phone number entered is not valid.'
            "</li></ul>",
            rendered_form,
        )
        self.assertInHTML(
            '<input type="text" name="phone_1" required id="id_phone_1">',
            rendered_form,
            count=1,
        )
        self.assertInHTML(
            '<option value="CA" selected>Canada +1</option>',
            rendered_form,
            count=1,
        )

    def test_keeps_region_with_invalid_national_number(self):
        form = self.form_class(data={"phone_0": "CA", "phone_1": "0000"})
        self.assertFalse(form.is_valid())
        rendered_form = str(form)
        self.assertInHTML(
            '<ul class="errorlist"><li>Enter a valid phone number (e.g. +12125552368).'
            "</li></ul>",
            rendered_form,
        )
        self.assertInHTML(
            '<input type="text" name="phone_1" value="0000" required id="id_phone_1">',
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
        widget = PhoneNumberPrefixWidget()
        html = widget.render(name="widget", value=None, attrs={"maxlength": 32})
        self.assertIn('<select name="widget_0">', html)

    def test_custom_attrs(self):
        widget = PhoneNumberPrefixWidget(
            country_attrs={"class": "country-input"},
            number_attrs={"class": "number-input"},
        )
        html = widget.render(name="widget", value=None)
        self.assertIn('<select name="widget_0" class="country-input">', html)
        self.assertInHTML(
            '<input type="text" name="widget_1" class="number-input">', html, count=1
        )


class PhoneNumberInternationalFallbackWidgetTest(SimpleTestCase):
    def test_fallback_widget_switches_between_national_and_international(self):
        region = "GB"
        number_string = "01606 751 78"
        number = PhoneNumber.from_string(number_string, region=region)
        gb_widget = PhoneNumberInternationalFallbackWidget(region="GB")
        de_widget = PhoneNumberInternationalFallbackWidget(region="DE")
        self.assertHTMLEqual(
            gb_widget.render("number", number),
            '<input name="number" type="text" value="01606 75178" />',
        )
        self.assertHTMLEqual(
            de_widget.render("number", number),
            '<input name="number" type="text" value="+44 1606 75178" />',
        )

        # If there's been a validation error, the value should be included verbatim
        self.assertHTMLEqual(
            gb_widget.render("number", "error"),
            '<input name="number" type="text" value="error" />',
        )
