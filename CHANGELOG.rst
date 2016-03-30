CHANGELOG
=========

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
