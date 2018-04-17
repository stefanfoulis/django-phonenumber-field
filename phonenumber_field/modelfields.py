from django.conf import settings
from django.core import checks
from django.db import models
from django.utils.encoding import force_text
from django.utils.translation import gettext_lazy as _

from phonenumber_field import formfields
from phonenumber_field.phonenumber import PhoneNumber, to_python, validate_region
from phonenumber_field.validators import validate_international_phonenumber
import functools


class PhoneNumberDescriptor:
    """
    The descriptor for the phone number attribute on the model instance.
    Returns a PhoneNumber when accessed so you can do stuff like::

        >>> instance.phone_number.as_international

    Assigns a phone number object on assignment so you can do::

        >>> instance.phone_number = PhoneNumber(...)

    or,

        >>> instance.phone_number = '+414204242'
    """

    def __init__(self, field):
        self.field = field

    def __get__(self, instance, owner):
        if instance is None:
            return self

        # The instance dict contains whatever was originally assigned in
        # __set__.
        if self.field.name in instance.__dict__:
            value = instance.__dict__[self.field.name]
        else:
            instance.refresh_from_db(fields=[self.field.name])
            value = getattr(instance, self.field.name)
        return value

    def __set__(self, instance, value):
        instance.__dict__[self.field.name] = to_python(value, region=self.field.region)


class PhoneNumberField(models.CharField):
    attr_class = PhoneNumber
    descriptor_class = PhoneNumberDescriptor

    description = _("Phone number")

<<<<<<< HEAD
    def __init__(self, *args, region=None, **kwargs):
        kwargs.setdefault("max_length", 128)
        super().__init__(*args, **kwargs)
        self.region = kwarge.pop('region', None)
        self.validators.append(validators.MaxLengthValidator(self.max_length))
        region_validator = functools.partial(validate_international_phonenumber, region=self.region)
        self.validators.append(region_validator)

    def check(self, **kwargs):
        errors = super().check(**kwargs)
        errors.extend(self._check_region())
        return errors

    def _check_region(self):
        try:
            validate_region(self.region)
        except ValueError as e:
            return [checks.Error(force_text(e), obj=self)]
        return []

    def get_prep_value(self, value):
        """
        Perform preliminary non-db specific value checks and conversions.
        """
        value = super().get_prep_value(value)
        value = to_python(value, region=self.region)
        if not isinstance(value, PhoneNumber):
            return value
        format_string = getattr(settings, 'PHONENUMBER_DB_FORMAT', 'E164')
        fmt = PhoneNumber.format_map[format_string]
        return value.format_as(fmt)

    def contribute_to_class(self, cls, name, *args, **kwargs):
        super().contribute_to_class(cls, name, *args, **kwargs)
        setattr(cls, self.name, self.descriptor_class(self))

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["region"] = self._region
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        defaults = {
            "form_class": formfields.PhoneNumberField,
            "region": self.region,
            "error_messages": self.error_messages,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)
