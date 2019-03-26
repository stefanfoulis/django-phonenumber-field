========================
django-phonenumber-field
========================

.. image:: https://travis-ci.org/stefanfoulis/django-phonenumber-field.svg?branch=master
    :target: https://travis-ci.org/stefanfoulis/django-phonenumber-field
.. image:: https://img.shields.io/coveralls/stefanfoulis/django-phonenumber-field/develop.svg
    :target: https://coveralls.io/github/stefanfoulis/django-phonenumber-field?branch=master

A Django library which interfaces with `python-phonenumbers`_ to validate, pretty print and convert
phone numbers. ``python-phonenumbers`` is a port of Google's `libphonenumber`_ library, which
powers Android's phone number handling.

.. _`python-phonenumbers`: https://github.com/daviddrysdale/python-phonenumbers
.. _`libphonenumber`: https://code.google.com/p/libphonenumber/

Included are:

* ``PhoneNumber``, a pythonic wrapper around ``python-phonenumbers``' ``PhoneNumber`` class
* ``PhoneNumberField``, a model field
* ``PhoneNumberField``, a form field
* ``PhoneNumberField``, a serializer field
* ``PhoneNumberPrefixWidget``, a form widget for selecting a region code and entering a national number
* ``PhoneNumberInternationalFallbackWidget``, a form widget that uses national numbers unless an
  international number is entered.  A ``PHONENUMBER_DEFAULT_REGION`` setting needs to be added
  to your Django settings in order to know which national number format to recognize.  The
  setting is a string containing an ISO-3166-1 two-letter country code.


Installation
============

::

    pip install django-phonenumber-field
    pip install phonenumbers

As an alternative to the ``phonenumbers`` package it is possible to install the
``phonenumberslite`` package which has
`a lower memory footprint <https://github.com/daviddrysdale/python-phonenumbers#memory-usage>`_.


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

The object returned is a PhoneNumber instance, not a string. If strings are used to initialize it,
e.g. via ``MyModel(phone_number='+41524204242')`` or form handling, it has to be a phone number
with country code.


Running tests
=============

tox needs to be installed. To run the whole test matrix with the locally
available Python interpreters and generate a combined coverage report::

    tox

run a specific combination::

    tox -e py36-dj21,py36-dj111
