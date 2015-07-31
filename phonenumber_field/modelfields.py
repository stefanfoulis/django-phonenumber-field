# -*- coding: utf-8 -*-

from django.conf import settings
from django.core import validators
from django.db import models
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.validators import validate_international_phonenumber
from phonenumber_field import formfields
from phonenumber_field.phonenumber import PhoneNumber, to_python, string_types
from django.core.exceptions import ValidationError


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

    def __get__(self, instance=None, owner=None):
        if instance is None:
            raise AttributeError(
                "The '%s' attribute can only be accessed from %s instances."
                % (self.field.name, owner.__name__))
        return instance.__dict__[self.field.name]

    def __set__(self, instance, value):
        instance.__dict__[self.field.name] = self.field.to_python(value)


class PhoneNumberField(models.Field):
    attr_class = PhoneNumber
    descriptor_class = PhoneNumberDescriptor
    default_validators = [validate_international_phonenumber]

    description = _("Phone number")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 131)# 128 for longest phone number + 2 for country id + 1 for comma
        super(PhoneNumberField, self).__init__(*args, **kwargs)
        self.validators.append(validators.MaxLengthValidator(self.max_length))
    
    def contribute_to_class(self, cls, name, **kwargs):
        super(PhoneNumberField, self).contribute_to_class(cls, name, **kwargs)
        setattr(cls, self.name, self.descriptor_class(self))

    def get_internal_type(self):
        return "CharField"

    def get_prep_value(self, value):
        "Returns field's value prepared for saving into a database."
        value = self.to_python(value)# PhoneNumber or None
        if isinstance(value, PhoneNumber):
            format_string = getattr(settings, 'PHONENUMBER_DB_FORMAT', 'E164')
            fmt = PhoneNumber.format_map[format_string]
            pieces = [value.format_as(fmt)]
            if value.country_id:
                pieces.insert(0, value.country_id)
            value = force_text(PhoneNumber.country_id_sep).join(pieces)
        else:
            if not self.null:
                value = force_text("")
        return value

    def to_python(self, value):
        if isinstance(value, string_types):
            value = to_python(value)
        if not (value is None or isinstance(value, PhoneNumber)):
            raise ValidationError("'%s' is an invalid value." % value)
        return value

    def formfield(self, **kwargs):
        defaults = {
            'form_class': formfields.PhoneNumberField,
        }
        defaults.update(kwargs)
        return super(PhoneNumberField, self).formfield(**defaults)

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([
        (
            [PhoneNumberField],
            [],
            {},
        ),
    ], ["^phonenumber_field\.modelfields\.PhoneNumberField"])
except ImportError:
    pass
