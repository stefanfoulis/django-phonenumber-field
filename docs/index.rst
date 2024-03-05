🕿 django-phonenumber-field 🕿
=============================

A `Django <https://www.djangoproject.com/>`_ library which interfaces with
`python-phonenumbers <https://github.com/daviddrysdale/python-phonenumbers>`_
to validate, pretty print and convert phone numbers. The python-phonenumbers
library is a port of Google’s `libphonenumber
<https://github.com/google/libphonenumber>`_ library, which powers Android’s
phone number handling.

Installation
============

Choosing a phonenumbers provider
--------------------------------

The `python-phonenumbers <https://github.com/daviddrysdale/python-phonenumbers>`_ library comes in `two flavors
<https://github.com/daviddrysdale/python-phonenumbers#memory-usage>`_:

.. code-block::

    # Installs phonenumbers minimal metadata
    pip install "django-phonenumber-field[phonenumberslite]"

.. code-block::

    # Installs phonenumbers extended features (e.g. geocoding)
    pip install "django-phonenumber-field[phonenumbers]"

Setup
-----

Add ``phonenumber_field`` to the list of the installed apps in
your ``settings.py`` file :external+django:setting:`INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = [
        # Other apps…
        "phonenumber_field",
    ]

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   phonenumbers
   reference
