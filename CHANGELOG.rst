CHANGELOG
=========

* Added the ``region`` keyword argument to ``PhoneNumberField``.
* Fix representation of invalid phone numbers in the database, previously
  stored as ``+NoneNone``. Now, invalid phone numbers are represented as:

  1. the field's `default`_ when it is specified, or
  2. empty ``str`` if the field is `blank`_ and not `null`_, or
  3. null.

  Existing database records can be upgraded with a `data migration`_.
* Added support for Django 2.2.
* Tests are now included in the sdist package.

.. _default: https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.Field.default
.. _blank: https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.Field.blank
.. _null: https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.Field.null
.. _data migration: https://docs.djangoproject.com/en/dev/topics/migrations/#data-migrations

2.2.0 (2019-01-27)
------------------

* Added support for null=True


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
* PhoneNumberField.get_prep_value changed to enable setting null=True
* new widget added: PhoneNumberInternationalFallbackWidget
* new backward compatible requirement phonenumberslite instead of phonenumbers
* lots of tests
* dropped support for PHONENUMER_DEFAULT_REGION setting with typo
