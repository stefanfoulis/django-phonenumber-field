========================
django-phonenumber-field
========================

.. image:: https://github.com/stefanfoulis/django-phonenumber-field/workflows/Test/badge.svg
    :target: https://github.com/stefanfoulis/django-phonenumber-field/workflows/Test/badge.svg
.. image:: https://img.shields.io/coveralls/stefanfoulis/django-phonenumber-field/develop.svg
    :target: https://coveralls.io/github/stefanfoulis/django-phonenumber-field?branch=main

A Django library which interfaces with `python-phonenumbers`_ to validate, pretty print and convert
phone numbers. ``python-phonenumbers`` is a port of Google's `libphonenumber`_ library, which
powers Android's phone number handling.

.. _`python-phonenumbers`: https://github.com/daviddrysdale/python-phonenumbers
.. _`libphonenumber`: https://github.com/google/libphonenumber

Documentation
=============

https://django-phonenumber-field.readthedocs.io/

Running tests
=============

tox needs to be installed. To run the whole test matrix with the locally
available Python interpreters and generate a combined coverage report::

    tox

run a specific combination::

    tox -e py310-djmain,py39-djmain
