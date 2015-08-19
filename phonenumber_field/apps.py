import warnings
from django.apps import AppConfig
from django.conf import settings

if hasattr(settings, "PHONENUMER_DEFAULT_REGION"):
    # Don't specify DeprecationWarning because it's output is hidden by default.  We want the user to see this warning by default.
    warnings.warn("The setting 'PHONENUMER_DEFAULT_REGION' is depreciated.  Use 'PHONENUMBER_DEFAULT_REGION' instead.", UserWarning)

class PhoneNumberFieldConfig(AppConfig):
    name = "phonenumber_field"
    verbose_name = "Phone Number Field"