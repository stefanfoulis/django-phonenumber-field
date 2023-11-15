Handling phone numbers
======================

`Google’s libphonenumber “Falsehoods Programmers Believe About Phone Numbers”
<https://github.com/google/libphonenumber/blob/master/FALSEHOODS.md>`_ are
worth keeping in mind, especially since this library relies heavily on
`libphonenumber <https://github.com/google/libphonenumber/>`_.

About phone numbers extensions
------------------------------

An extension is an additional phone line added to an existing phone system,
making it possible to reach a specific employee or department within an
organization. An extension is defined in the following manner:

.. doctest:: extensions

   >>> import phonenumbers
   >>> phonenumbers.parse("+1 604-401-1234 ext. 987")
   PhoneNumber(country_code=1, national_number=6044011234, extension='987', italian_leading_zero=None, number_of_leading_zeros=None, country_code_source=0, preferred_domestic_carrier_code=None)
   >>> phonenumbers.parse("+1 604-401-1234,987")
   PhoneNumber(country_code=1, national_number=6044011234, extension='987', italian_leading_zero=None, number_of_leading_zeros=None, country_code_source=0, preferred_domestic_carrier_code=None)

The library primarily focuses on public phone numbers, its default format and
database representation are using `E.164
<https://en.wikipedia.org/wiki/E.164>`_, which has no support for extensions.

Projects that need to handle phone number extensions must set **both**
:setting:`PHONENUMBER_DEFAULT_FORMAT` and :setting:`PHONENUMBER_DB_FORMAT` to
an extension-compatible format, as described in
:ref:`settings-format-choices`.
