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

::

    pip install django-phonenumber-field


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
