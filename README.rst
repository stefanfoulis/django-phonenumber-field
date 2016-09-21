========================
django-phonenumber-field
========================

.. image:: https://img.shields.io/travis/stefanfoulis/django-phonenumber-field/develop.svg
    :target: https://travis-ci.org/stefanfoulis/django-phonenumber-field
.. image:: https://img.shields.io/coveralls/stefanfoulis/django-phonenumber-field/develop.svg
    :target: https://coveralls.io/github/stefanfoulis/django-phonenumber-field?branch=develop

A Django library which interfaces with `python-phonenumbers`_ to validate, pretty print and convert
phone numbers. ``python-phonenumbers`` is a port of Google's `libphonenumber`_ library, which
powers Android's phone number handling.

.. _`python-phonenumbers`: https://github.com/daviddrysdale/python-phonenumbers
.. _`libphonenumber`: https://code.google.com/p/libphonenumber/

Included are:

* ``PhoneNumber``, a pythonic wrapper around ``python-phonenumbers``' ``PhoneNumber`` class
* ``PhoneNumberField``, a model field
* ``PhoneNumberField``, a form field
* ``PhoneNumberPrefixWidget``, a form widget for selecting a region code and entering a national number
* ``PhoneNumberInternationalFallbackWidget``, a form widget that uses national numbers unless an international number is entered

*Note:* This package will by default install `phonenumberslite` if no
 phonenumbers package has been installed already.

Installation
============

::

    pip install django-phonenumber-field


Basic usage
===========

First, add ``phonenumber_field`` to the list of the installed apps in 
your ``settings.py`` file::

    INSTALLED_APPS = [
        ...
        'phonenumber_field',
        ...
    ]

Then, you can use it like any regular model field::

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
