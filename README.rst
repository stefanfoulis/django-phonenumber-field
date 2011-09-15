========================
django-phonenumber-field
========================


A international phone number field for django that uses http://pypi.python.org/pypi/phonenumbers for validation .

Installation
============

::

    pip install django-phonenumber-field


Basic usage
===========

Use it like any regular model field::

    from phonenumber_field.modelfields import PhoneNumberField
    class MyModel(models.Model):
        name = models.CharField(max_length=255)
        phone_number = PhoneNumberField()
        fax_number = PhoneNumberField(null=True, blank=True)

PhoneNumberField will always represent the number as a string of an international phonenumber in the database. E.g
`+41524204242`.

The object returned is not just a plain String. It is a PhoneNumber object. Currently it is necessary to always use
the international format when entering data. 

Future versions of django-phonenumber-field may provide custom special widgets that support more custom formatting.

