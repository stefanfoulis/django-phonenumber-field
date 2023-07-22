import warnings

from django.conf import settings
from django.core import validators
from django.core.exceptions import ImproperlyConfigured
from django.forms import Select, TextInput
from django.forms.widgets import MultiWidget
from django.utils import translation
from phonenumbers import (
    COUNTRY_CODE_TO_REGION_CODE,
    national_significant_number,
    region_code_for_number,
    region_codes_for_country_code,
)

from phonenumber_field.phonenumber import PhoneNumber, to_python

try:
    import babel
except ModuleNotFoundError:
    babel = None  # type: ignore

# ISO 3166-1 alpha-2 to national prefix
REGION_CODE_TO_COUNTRY_CODE = {
    region_code: country_code
    for country_code, region_codes in COUNTRY_CODE_TO_REGION_CODE.items()
    for region_code in region_codes
}


def localized_choices(language):
    if babel is None:
        raise ImproperlyConfigured(
            "The PhonePrefixSelect widget requires the babel package be installed."
        )

    choices = [("", "---------")]
    locale_name = translation.to_locale(language)
    locale = babel.Locale(locale_name)
    for region_code, country_code in REGION_CODE_TO_COUNTRY_CODE.items():
        region_name = locale.territories.get(region_code)
        if region_name:
            choices.append((region_code, f"{region_name} +{country_code}"))
    return choices


class PhonePrefixSelect(Select):
    initial = None

    def __init__(self, initial=None, attrs=None, choices=None):
        language = translation.get_language() or settings.LANGUAGE_CODE
        if choices is None:
            choices = localized_choices(language)
            choices.sort(key=lambda item: item[1])
        if initial is None:
            initial = getattr(settings, "PHONENUMBER_DEFAULT_REGION", None)
        if initial in REGION_CODE_TO_COUNTRY_CODE:
            self.initial = initial
        super().__init__(attrs=attrs, choices=choices)

    def get_context(self, name, value, attrs):
        attrs = (attrs or {}).copy()
        attrs.pop("maxlength", None)
        return super().get_context(name, value or self.initial, attrs)


class PhoneNumberPrefixWidget(MultiWidget):
    """
    A Widget that splits a phone number into fields:

    - a :class:`~django.forms.Select` for the country (phone prefix)
    - a :class:`~django.forms.TextInput` for local phone number
    """

    def __init__(
        self,
        attrs=None,
        initial=None,
        country_attrs=None,
        country_choices=None,
        number_attrs=None,
    ):
        """
        :keyword dict attrs: See :attr:`~django.forms.Widget.attrs`
        :keyword dict initial: See :attr:`~django.forms.Field.initial`
        :keyword dict country_attrs: The :attr:`~django.forms.Widget.attrs` for
            the country :class:`~django.forms.Select`.
        :keyword country_choices: Limit the country choices.
        :type country_choices: list of 2-tuple, optional
            The first element is the value, which must match a country code
            recognized by the phonenumbers project.
            The second element is the label.
        :keyword dict number_attrs: The :attr:`~django.forms.Widget.attrs` for
            the local phone number :class:`~django.forms.TextInput`.
        """
        widgets = (
            PhonePrefixSelect(initial, attrs=country_attrs, choices=country_choices),
            TextInput(attrs=number_attrs),
        )
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if isinstance(value, PhoneNumber):
            if not value.is_valid():
                region = getattr(settings, "PHONENUMBER_DEFAULT_REGION", None)
                region_code = getattr(value, "_region", region)
                return [region_code, value.raw_input]
            region_code = region_code_for_number(value)
            national_number = national_significant_number(value)
            return [region_code, national_number]
        return [None, None]

    def value_from_datadict(self, data, files, name):
        region_code, national_number = super().value_from_datadict(data, files, name)

        if national_number is None:
            national_number = ""
        number = to_python(national_number, region=region_code)
        if number in validators.EMPTY_VALUES:
            return number
        number._region = region_code
        return number


class RegionalPhoneNumberWidget(TextInput):
    """
    A :class:`~django.forms.Widget` that prefers displaying numbers in the
    national format, and falls back to :setting:`PHONENUMBER_DEFAULT_FORMAT`
    for international numbers.
    """

    input_type = "tel"

    def __init__(self, region=None, attrs=None):
        """
        :keyword str region: 2-letter country code as defined in ISO 3166-1.
            When not supplied, defaults to :setting:`PHONENUMBER_DEFAULT_REGION`
        :keyword dict attrs: See :attr:`django.forms.Widget.attrs`
        """
        if region is None:
            region = getattr(settings, "PHONENUMBER_DEFAULT_REGION", None)
        self.region = region
        super().__init__(attrs)

    def value_from_datadict(self, data, files, name):
        phone_number_str = super().value_from_datadict(data, files, name)

        if phone_number_str is None:
            phone_number_str = ""
        return to_python(phone_number_str, region=self.region)

    def format_value(self, value):
        if isinstance(value, PhoneNumber):
            if value.is_valid() and value.country_code:
                region_codes = region_codes_for_country_code(value.country_code)
                if self.region in region_codes:
                    return value.as_national
        return super().format_value(value)


class PhoneNumberInternationalFallbackWidget(RegionalPhoneNumberWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        warnings.warn(
            f"{self.__class__.__name__} will be removed in the next major version. "
            "Use phonenumber_field.widgets.RegionalPhoneNumberWidget instead.",
            DeprecationWarning,
            stacklevel=2,
        )

    def format_value(self, value):
        if isinstance(value, PhoneNumber):
            if value.is_valid() and value.country_code:
                region_codes = region_codes_for_country_code(value.country_code)
                if self.region in region_codes:
                    return value.as_national
                return value.as_international
        return super().format_value(value)
