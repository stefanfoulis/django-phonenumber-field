CHANGELOG
=========

4.0.0 (2019-12-06)
------------------

The big version bump is due to the change in how invalid phone numbers are handled.
Starting with ``2.4.0`` we added very aggressive validation, which raised ``ValueError``
for invalid numbers. This caused problems in unexpected places (like when filtering a
queryset). Starting with ``4.0.0`` we acknowledge that we can not completely prevent
invalid numbers from entering the system. Changes directly to the database, validation
changes in the upstream phonenumbers library, changes in the django settings may all
lead to invalid numbers in the database. Now it is possible to save an invalid number
to the database and ``__str__`` and ``__repr__`` clearly indicate invalid numbers.

* Don’t raise ``ValueError`` on invalid phone numbers - ``__str__`` and ``__repr__``
  updated to report invalid phone numbers correctly if detected.
* Various translation updates

3.0.1 (2019-05-28)
------------------

* Allow overriding the default invalid phone number message.

3.0.0 (2019-05-28)
------------------

* Update French and Hebrew translations.
* Add a valid phone number example to invalid phone number error messages.

**Backwards incompatible changes**

* Drop support for Django 2.0.
* Drop support for Python 2.7 and 3.4.

2.4.0 (2019-05-06)
------------------

* A ``PhoneNumberField`` can now be deferred with ``QuerySet.defer()``.
* Saving or filtering by an invalid phone number will now raise a
  ``ValueError``.
* The model field attribute ``PhoneNumberField.region`` now uses
  ``PHONENUMBER_DEFAULT_REGION`` if not specified.

2.3.1 (2019-03-26)
------------------

* Fixed a regression to re-allow the model field to override the default form
  field.

2.3.0 (2019-03-26)
------------------

* Added the ``region`` keyword argument to ``PhoneNumberField``.
* Fix representation of invalid phone numbers in the database, previously
  stored as ``+NoneNone``. Now, invalid phone numbers are represented as:

  1. the field's `default`_ when it is specified, or
  2. empty ``str`` if the field is `blank`_ and not `null`_, or
  3. null.

  Existing database records can be upgraded with a `data migration`_.
* Added support for Django 2.2.
* Tests are now included in the sdist package.
* ``modelfields.PhoneNumberField`` now inherits from ``models.CharField``
  instead of ``models.Field``.

.. _default: https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.Field.default
.. _blank: https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.Field.blank
.. _null: https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.Field.null
.. _data migration: https://docs.djangoproject.com/en/dev/topics/migrations/#data-migrations

2.2.0 (2019-01-27)
------------------

* Added support for ``null=True``


2.1.0 (2018-10-28)
------------------

* Removed hardcoded dependency to phonenumbers library. Now developers have to
  manually install either phonenumbers or phonenumberslite.
* Added Romanian locale
* Added Bangla locale
* Update French locale
* Update Italian locale


2.0.1 (2018-08-19)
------------------

* Statically depend on phonenumbers
  Previously the phonenumberslight dependency was used dynamically in setup.py
  if it already was installed, causing problems with building wheels and
  with pipenv.
* Added Ukrainian locale
* Added Simplified Chinese locale


2.0.0 (2018-01-04)
------------------

* Add Django 2.0 support
* Drop Support for Django<1.11
* Translations: Swedish


1.3.0 (2017-04-15)
------------------

* Add rest_framework Serializer
* Hashable phonenumber object
* Various bugfixes and improvements


1.2.0 (2017-03-17)
------------------

* Django 1.10 support
* Bugfixes and cleanup
* Translations: Brazilian Portuguese, Spanish, Norwegian, Dutch, Azerbaijani, Turkish and French


1.1.0 (2016-03-30)
------------------

* Django 1.9 support
* README updated and links fixed
* support for HTML5.0 tel input type added
* locale files are now included
* new translations: Danish, Esperanto, Polish, all translations reformatted, Russian translation expanded
* PhoneNumberField.get_prep_value changed to enable setting ``null=True``
* new widget added: ``PhoneNumberInternationalFallbackWidget``
* new backward compatible requirement phonenumberslite instead of phonenumbers
* lots of tests
* dropped support for ``PHONENUMER_DEFAULT_REGION`` setting with typo
