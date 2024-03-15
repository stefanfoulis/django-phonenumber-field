from django.test import SimpleTestCase, override_settings

from phonenumber_field.phonenumber import PhoneNumber
from phonenumber_field.widgets import RegionalPhoneNumberWidget


class RegionalPhoneNumberWidgetTest(SimpleTestCase):
    @override_settings(PHONENUMBER_DEFAULT_FORMAT="INTERNATIONAL")
    def test_fallback_widget_switches_between_national_and_international(self):
        region = "GB"
        number_string = "01606 751 78"
        number = PhoneNumber.from_string(number_string, region=region)
        gb_widget = RegionalPhoneNumberWidget()
        gb_widget.region = "GB"
        de_widget = RegionalPhoneNumberWidget()
        de_widget.region = "DE"
        self.assertHTMLEqual(
            gb_widget.render("number", number),
            '<input name="number" type="tel" value="01606 75178" />',
        )
        self.assertHTMLEqual(
            de_widget.render("number", number),
            '<input name="number" type="tel" value="+44 1606 75178" />',
        )

        # If there's been a validation error, the value should be included verbatim
        self.assertHTMLEqual(
            gb_widget.render("number", "error"),
            '<input name="number" type="tel" value="error" />',
        )

    def test_fallback_defaults_to_phonenumber_default_format(self):
        region = "GB"
        number_string = "01606 751 78"
        number = PhoneNumber.from_string(number_string, region=region)
        widget = RegionalPhoneNumberWidget(region="FR")
        for fmt, expected in [
            ("INTERNATIONAL", "+44 1606 75178"),
            ("E164", "+44160675178"),
            ("RFC3966", "tel:+44-1606-75178"),
        ]:
            with self.subTest(fmt):
                with override_settings(PHONENUMBER_DEFAULT_FORMAT=fmt):
                    self.assertHTMLEqual(
                        widget.render("number", number),
                        f'<input name="number" type="tel" value="{expected}" />',
                    )

    def test_no_region(self):
        number_string = "+33612345678"
        number = PhoneNumber.from_string(number_string)
        widget = RegionalPhoneNumberWidget()
        for fmt, expected in [
            ("INTERNATIONAL", "+33 6 12 34 56 78"),
            ("E164", "+33612345678"),
            ("RFC3966", "tel:+33-6-12-34-56-78"),
        ]:
            with self.subTest(fmt):
                with override_settings(PHONENUMBER_DEFAULT_FORMAT=fmt):
                    self.assertHTMLEqual(
                        widget.render("number", number),
                        f'<input name="number" type="tel" value="{expected}" />',
                    )
