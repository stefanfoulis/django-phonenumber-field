.. testsetup:: *

   import django
   from bs4 import BeautifulSoup

   django.setup()

   def print_html(html):
       print(BeautifulSoup(html).prettify().strip())

   def print_html_compact(html):
       output = BeautifulSoup(html).prettify().strip().splitlines()
       print("\n".join(output[:15]))
       print("   ...")
       print("\n".join(output[-7:]))


The PhoneNumber wrapper
=======================

.. autoclass:: phonenumber_field.phonenumber.PhoneNumber()

   .. automethod:: phonenumber_field.phonenumber.PhoneNumber.from_string

   .. automethod:: phonenumber_field.phonenumber.PhoneNumber.is_valid

   .. autoproperty:: phonenumber_field.phonenumber.PhoneNumber.as_international

   .. autoproperty:: phonenumber_field.phonenumber.PhoneNumber.as_national

   .. autoproperty:: phonenumber_field.phonenumber.PhoneNumber.as_e164

   .. autoproperty:: phonenumber_field.phonenumber.PhoneNumber.as_rfc3966

Usage
-----

.. doctest:: wrapper

   >>> from phonenumber_field.phonenumber import PhoneNumber

   >>> number = PhoneNumber.from_string("+16044011234")
   >>> print(number.as_national)
   (604) 401-1234
   >>> print(number.as_e164)
   +16044011234
   >>> print(number.as_international)
   +1 604-401-1234
   >>> print(number.as_rfc3966)
   tel:+1-604-401-1234

   # Using national numbers with the region keyword argument.
   >>> canadian_number = "(604) 401 1234"
   >>> number = PhoneNumber.from_string(canadian_number, region="CA")
   >>> print(number.as_e164)
   +16044011234

Model field
===========

The :class:`~phonenumber_field.modelfields.PhoneNumberField` :ref:`model field
<topics/db/models:fields>` allows storing
:class:`~phonenumber_field.phonenumber.PhoneNumber`\ s in the database, based
on a :class:`~django.db.models.CharField`.

The phone number format used by the database is controlled with
:setting:`PHONENUMBER_DB_FORMAT`. When no region is specified, a phone number
in the ``"NATIONAL"`` format will be assumed to be from the
:setting:`PHONENUMBER_DEFAULT_REGION`.

- The default :ref:`form field <ref/forms/fields:form fields>` for this field is
  the :class:`~phonenumber_field.formfields.PhoneNumberField`.
- The default :ref:`form widget <ref/forms/widgets:widgets>` for this field is
  the :class:`~phonenumber_field.widgets.RegionalPhoneNumberWidget`.

.. autoclass:: phonenumber_field.modelfields.PhoneNumberField

   .. automethod:: __init__

Usage
-----

.. code-block:: python

   from django.db import models
   from phonenumber_field.modelfields import PhoneNumberField


   class Customer(models.Model):
       name = models.TextField()
       # An optional phone number.
       phone_number = PhoneNumberField(blank=True)

Form fields
===========

:class:`~phonenumber_field.formfields.PhoneNumberField`
-------------------------------------------------------

The :class:`~phonenumber_field.formfields.PhoneNumberField` :ref:`form field
<ref/forms/fields:form fields>` to validate
:class:`~phonenumber_field.phonenumber.PhoneNumber`, based on a
:class:`~django.forms.CharField`.

- Default widget: :class:`~phonenumber_field.widgets.RegionalPhoneNumberWidget`
- Empty value: ``""``
- Normalizes to: A :class:`~phonenumber_field.phonenumber.PhoneNumber` or an
  empty :class:`str` (``""``)
- Uses :func:`~phonenumber_field.validators.validate_international_phonenumber`

.. autoclass:: phonenumber_field.formfields.PhoneNumberField

   .. automethod:: __init__

Usage
~~~~~

.. doctest:: formfield

   >>> from django import forms
   >>> from phonenumber_field.formfields import PhoneNumberField

   >>> class PhoneForm(forms.Form):
   ...     number = PhoneNumberField(region="CA")
   ...

   # Manipulating data
   >>> form = PhoneForm({"number": "+1 604 401 1234"})
   >>> form.is_valid()
   True
   >>> form.cleaned_data
   {'number': PhoneNumber(country_code=1, national_number=6044011234, extension=None, italian_leading_zero=None, number_of_leading_zeros=None, country_code_source=1, preferred_domestic_carrier_code=None)}
   >>> print_html(form.as_div())
   <div>
    <label for="id_number">
     Number:
    </label>
    <input id="id_number" name="number" required="" type="tel" value="(604) 401-1234"/>
   </div>

   # Handling errors
   >>> form = PhoneForm({"number": "invalid"})
   >>> form.is_valid()
   False
   >>> print_html(form.as_div())
   <div>
    <label for="id_number">
     Number:
    </label>
    <ul class="errorlist">
     <li>
      Enter a valid phone number (e.g. (506) 234-5678) or a number with an international call prefix.
     </li>
    </ul>
    <input aria-invalid="true" id="id_number" name="number" required="" type="tel" value="invalid"/>
   </div>

.. note:: Because the PhoneNumberField specifies a region, the example number
   is a national number from that region. When no region is specified, an
   international example phone number in the E.164 format is suggested.


:class:`~phonenumber_field.formfields.SplitPhoneNumberField`
------------------------------------------------------------

A :class:`~django.forms.MultiValueField` that offers:

- a ``<select … >`` element to choose the region, and
- an ``<input type="tel" … >`` to enter the phone number.

This widget uses an example phone number from the selected region for the
``invalid`` key in :attr:`~django.forms.Field.error_messages`, when the region
choice is valid.

To customize the dynamic message, use
:func:`phonenumber_field.formfields.SplitPhoneNumberField.invalid_error_message`.

.. important:: Requires the `Babel <https://pypi.org/project/Babel/>`_ package.

.. autoclass:: phonenumber_field.formfields.SplitPhoneNumberField

   .. automethod:: __init__
   .. automethod:: invalid_error_message

Usage
~~~~~

.. doctest:: SplitPhoneNumberField

   >>> from django import forms
   >>> from phonenumber_field.formfields import SplitPhoneNumberField

   >>> class PhoneForm(forms.Form):
   ...     number = SplitPhoneNumberField()
   ...

   >>> form = PhoneForm()
   >>> print_html_compact(form.as_div())
   <div>
    <fieldset>
     <legend>
      Number:
     </legend>
     <select id="id_number_0" name="number_0" required="">
      <option selected="" value="">
       ---------
      </option>
      <option value="AF">
       Afghanistan +93
      </option>
      <option value="AL">
       Albania +355
      </option>
      ...
      <option value="AX">
       Åland Islands +358
      </option>
     </select>
     <input id="id_number_1" name="number_1" required="" type="tel"/>
    </fieldset>
   </div>

   # Limiting country choices.
   >>> class DemoSplitPhoneNumberField(SplitPhoneNumberField):
   ...     def prefix_field(self):
   ...         return forms.ChoiceField(choices=[
   ...             ("", "---------"),
   ...             ("CA", "Canada"),
   ...             ("FR", "France"),
   ...         ])
   ...
   >>> class LimitedCountryPhoneForm(forms.Form):
   ...     number = DemoSplitPhoneNumberField()
   ...
   >>> form = LimitedCountryPhoneForm()
   >>> print_html(form.as_div())
   <div>
    <fieldset>
     <legend>
      Number:
     </legend>
     <select id="id_number_0" name="number_0" required="">
      <option selected="" value="">
       ---------
      </option>
      <option value="CA">
       Canada
      </option>
      <option value="FR">
       France
      </option>
     </select>
     <input id="id_number_1" name="number_1" required="" type="tel"/>
    </fieldset>
   </div>

   # Pre-selecting a country.
   >>> class FrenchPhoneForm(forms.Form):
   ...     number = DemoSplitPhoneNumberField(region="FR")
   ...

   >>> form = FrenchPhoneForm()
   >>> print_html(form.as_div())
   <div>
    <fieldset>
     <legend>
      Number:
     </legend>
     <select id="id_number_0" name="number_0" required="">
      <option value="">
       ---------
      </option>
      <option value="CA">
       Canada
      </option>
      <option selected="" value="FR">
       France
      </option>
     </select>
     <input id="id_number_1" name="number_1" required="" type="tel"/>
    </fieldset>
   </div>

Widgets
-------

RegionalPhoneNumberWidget
~~~~~~~~~~~~~~~~~~~~~~~~~

**Default widget** for :class:`~phonenumber_field.formfields.PhoneNumberField`.

- input_type: ``tel``
- Renders as ``<input type="tel" … >``

.. important:: The region should be specified (either per field using the
   ``region`` keyword argument, or with the
   :setting:`PHONENUMBER_DEFAULT_REGION` setting) in order to know which
   national number format to recognize.


.. autoclass:: phonenumber_field.widgets.RegionalPhoneNumberWidget

   .. automethod:: __init__

Usage
.....

.. doctest:: fallbackwidget

   >>> from django import forms
   >>> from phonenumber_field.formfields import PhoneNumberField

   >>> class CanadianPhoneForm(forms.Form):
   ...     # RegionalPhoneNumberWidget is the default widget.
   ...     number = PhoneNumberField(region="CA")
   ...

   # Using the national format for the field’s region.
   >>> form = CanadianPhoneForm({"number": "+16044011234"})
   >>> print_html(form.as_div())
   <div>
    <label for="id_number">
     Number:
    </label>
    <input id="id_number" name="number" required="" type="tel" value="(604) 401-1234"/>
   </div>

   # Using E164 for an international number.
   >>> french_number = "+33612345678"
   >>> form = CanadianPhoneForm({"number": french_number})
   >>> print_html(form.as_div())
   <div>
    <label for="id_number">
     Number:
    </label>
    <input id="id_number" name="number" required="" type="tel" value="+33612345678"/>
   </div>

PhoneNumberPrefixWidget
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: phonenumber_field.widgets.PhoneNumberPrefixWidget

Serializer field
================

The :class:`~phonenumber_field.serializersfields.PhoneNumberField` `serializer
field <https://www.django-rest-framework.org/api-guide/fields/>`_, based on the
`CharField
<https://www.django-rest-framework.org/api-guide/fields/#charfield>`_.

The serialization format is controlled by the
:setting:`PHONENUMBER_DEFAULT_FORMAT`.

.. autoclass:: phonenumber_field.serializerfields.PhoneNumberField

   .. automethod:: __init__

Usage
-----

.. doctest:: serializerfield

    >>> from django.conf import settings
    >>> from rest_framework import renderers, serializers
    >>> from phonenumber_field.serializerfields import PhoneNumberField

    >>> class PhoneNumberSerializer(serializers.Serializer):
    ...     number = PhoneNumberField(region="CA")
    ...

    >>> serializer = PhoneNumberSerializer(data={"number": "604 401 1234"})
    >>> serializer.is_valid()
    True
    >>> serializer.validated_data
    {'number': PhoneNumber(country_code=1, national_number=6044011234, extension=None, italian_leading_zero=None, number_of_leading_zeros=None, country_code_source=20, preferred_domestic_carrier_code=None)}

    # Using the PHONENUMBER_DEFAULT_FORMAT.
    >>> renderers.JSONRenderer().render(serializer.data)
    b'{"number":"+16044011234"}'


Validator
=========

Validates:

- a :class:`~phonenumber_field.phonenumber.PhoneNumber` instance, or
- an :class:`str` in an international format (with a prefix), or
- an :class:`str` that’s a local phone number according to
  :setting:`PHONENUMBER_DEFAULT_REGION`.

.. note:: Not all well-formed phone numbers are valid. The rules to construct
   phone numbers vary per region of the world.

   `Falsehoods Programmers Believe About Phone Numbers
   <https://github.com/google/libphonenumber/blob/master/FALSEHOODS.md>`_ is a
   good read.

.. autofunction:: phonenumber_field.validators.validate_international_phonenumber

**code**: ``"invalid"``

Settings
========

.. _settings-format-choices:

Phone number format choices
---------------------------

+------------------------+---------------+------------+-----------------------------------------------------------------+
| Setting value          | International | Extensions | Notes                                                           |
+========================+===============+============+=================================================================+
| ``"E164"`` *(default)* | ✓             | ❌         | https://en.wikipedia.org/wiki/E.164                             |
+------------------------+---------------+------------+-----------------------------------------------------------------+
| ``"INTERNATIONAL"``    | ✓             | ✓          | https://en.wikipedia.org/wiki/E.123#Telephone_number            |
+------------------------+---------------+------------+-----------------------------------------------------------------+
| ``"RFC3966"``          | ✓             | ✓          | https://www.rfc-editor.org/rfc/rfc3966.html                     |
+------------------------+---------------+------------+-----------------------------------------------------------------+
| ``"NATIONAL"``         | ❌            | ✓          | **DISCOURAGED**, requires :setting:`PHONENUMBER_DEFAULT_REGION` |
+------------------------+---------------+------------+-----------------------------------------------------------------+

.. warning::

    By default, the library uses `E.164, the international public
    telecommunication numbering plan <https://en.wikipedia.org/wiki/E.164>`_,
    which **does not support phone numbers extensions**. Set **both**
    :setting:`PHONENUMBER_DB_FORMAT` and :setting:`PHONENUMBER_DEFAULT_FORMAT`
    to an extension-compatible format to handle phone numbers extensions.

.. setting:: PHONENUMBER_DB_FORMAT

``PHONENUMBER_DB_FORMAT``
-------------------------

Store phone numbers strings in the specified format in the database.

Default: ``"E164"``.

See :ref:`settings-format-choices`.

.. warning:: **Data loss may occur when changing the DB format.**

   Phone numbers stored in the database are parsed every time they are loaded
   from the database.

   When switching from a format that can represent extensions to a format that
   cannot, the **extension information is definitely lost**.

   When using :setting:`PHONENUMBER_DB_FORMAT`\ ``="NATIONAL"``, changing the
   :setting:`PHONENUMBER_DEFAULT_REGION` will cause phone numbers stored in the
   database to be interpreted differently, resulting in data corruption.

.. setting:: PHONENUMBER_DEFAULT_FORMAT

``PHONENUMBER_DEFAULT_FORMAT``
------------------------------

String formatting of phone numbers.

Default: ``"E164"``.

See :ref:`settings-format-choices`.

.. setting:: PHONENUMBER_DEFAULT_REGION

``PHONENUMBER_DEFAULT_REGION``
------------------------------

`ISO-3166-1 <https://en.wikipedia.org/wiki/ISO_3166-1#Current_codes>`_
two-letter country code indicating how to interpret regional phone numbers.

Default: ``None``.
