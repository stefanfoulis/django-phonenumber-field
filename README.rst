========================
django-phonenumber-field
========================

.. image:: https://travis-ci.org/GaretJax/django-phonenumber-field.svg?branch=develop
    :target: https://travis-ci.org/GaretJax/django-phonenumber-field
.. image:: https://coveralls.io/repos/GaretJax/django-phonenumber-field/badge.png?branch=develop
    :target: https://coveralls.io/r/GaretJax/django-phonenumber-field?branch=develop

A Django library which interfaces with `python-phonenumbers`_ to validate, pretty print and convert
phone numbers. ``python-phonenumbers`` is a port of Google's `libphonenumber`_ library, which powers Android's phone number handling.

.. _`python-phonenumbers`: https://github.com/daviddrysdale/python-phonenumbers
.. _`libphonenumber`: https://code.google.com/p/libphonenumber/

Included are:

* ``PhoneNumber``, a pythonic wrapper around ``python-phonenumbers``' ``PhoneNumber`` class
* ``PhoneNumberField``, a model field
* ``PhoneNumberField``, a form field
* ``PhoneNumberPrefixWidget``, a form widget

Installation
============

To install django-phonenumber-field use your favorite packaging tool, e.g.pip:

::

    pip install django-phonenumber-field

Then add 'phonenumber_field' to your INSTALLED_APPS setting:

::

    INSTALLED_APPS = (
        # ...
        'phonenumber_field',
    )

To make use of the supplied widget, migrate and populate the database:

::

    python manage.py migrate
    python manage.py autopopulate_phonenumber_field_models

Note that the database will automatically be populated when the PhoneNumber widget
is rendered and no CountryCode instances exist in the database.  However, you must
manually run the management command when updating in order for the database to reflect
changes to the choices available from the underlying ``python-phonenumbers`` package.

Basic usage
===========

Use it like any regular model field::

    from phonenumber_field.modelfields import PhoneNumberField

    class MyModel(models.Model):
        name = models.CharField(max_length=255)
        phone_number = PhoneNumberField()
        fax_number = PhoneNumberField(blank=True)

Internally, PhoneNumberField is based upon ``CharField`` and by default
represents the number as a string of an international phonenumber in the database (e.g
``'+41524204242'``).

Representation can be set by ``PHONENUMBER_DB_FORMAT`` variable in django settings module.
This variable must be one of  ``'E164'``, ``'INTERNATIONAL'``, ``'NATIONAL'`` or ``'RFC3966'``.
Recommended is one of the globally meaningful formats  ``'E164'``, ``'INTERNATIONAL'`` or
``'RFC3966'``. ``'NATIONAL'`` format require to set up ``PHONENUMBER_DEFAULT_REGION`` variable.

As with ``CharField``'s, it is discouraged to use ``null=True``.

The object returned is a PhoneNumber instance, not a string. If strings are used to initialize it,
e.g. via ``MyModel(phone_number='+41524204242')`` or form handling, it has to be a phone number
with country code.

Country Codes displayed to the user by the default widget can be controlled via the admin site by
setting the ``active`` field on any of the RegionCode, CallingCode, or CountryCode model instances.
