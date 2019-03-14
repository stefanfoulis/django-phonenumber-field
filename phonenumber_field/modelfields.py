# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core import checks, validators
from django.db import connection, models
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from phonenumber_field import formfields
from phonenumber_field.phonenumber import PhoneNumber, to_python, validate_region
from phonenumber_field.validators import validate_international_phonenumber


class PhoneNumberDescriptor(object):
    """
    The descriptor for the phone number attribute on the model instance.
    Returns a PhoneNumber when accessed so you can do stuff like::

        >>> instance.phone_number.as_international

    Assigns a phone number object on assignment so you can do::

        >>> instance.phone_number = PhoneNumber(...)
    or
        >>> instance.phone_number = '+414204242'
    """

    def __init__(self, field):
        self.field = field

    def __get__(
        self, instance=None, owner=None
    ):  # lgtm [py/special-method-wrong-signature]
        if instance is None:
            return self
        return instance.__dict__[self.field.name]

    def __set__(self, instance, value):
        instance.__dict__[self.field.name] = to_python(value, region=self.field.region)


class PhoneNumberField(models.Field):
    attr_class = PhoneNumber
    descriptor_class = PhoneNumberDescriptor
    default_validators = [validate_international_phonenumber]

    description = _("Phone number")

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 128)
        self.region = kwargs.pop("region", None)
        super(PhoneNumberField, self).__init__(*args, **kwargs)
        self.validators.append(validators.MaxLengthValidator(self.max_length))

    def check(self, **kwargs):
        errors = super(PhoneNumberField, self).check(**kwargs)
        errors.extend(self._check_region())
        return errors

    def _check_region(self):
        try:
            validate_region(self.region)
        except ValueError as e:
            return [checks.Error(force_text(e), obj=self)]
        return []

    def get_internal_type(self):
        return "CharField"

    def get_prep_value(self, value):
        """
        Perform preliminary non-db specific value checks and conversions.
        """
        value = super(PhoneNumberField, self).get_prep_value(value)
        value = to_python(value)
        if not isinstance(value, PhoneNumber):
            return value
        format_string = getattr(settings, "PHONENUMBER_DB_FORMAT", "E164")
        fmt = PhoneNumber.format_map[format_string]
        return value.format_as(fmt)

    def contribute_to_class(self, cls, name, *args, **kwargs):
        super(PhoneNumberField, self).contribute_to_class(cls, name, *args, **kwargs)
        setattr(cls, self.name, self.descriptor_class(self))

    def deconstruct(self):
        name, path, args, kwargs = super(PhoneNumberField, self).deconstruct()
        kwargs["region"] = self.region
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        defaults = {
            "form_class": formfields.PhoneNumberField,
            "region": self.region,
            "error_messages": self.error_messages,
        }

        if self.null and not connection.features.interprets_empty_strings_as_nulls:
            defaults["empty_value"] = None

        defaults.update(kwargs)
        return super(PhoneNumberField, self).formfield(**defaults)
