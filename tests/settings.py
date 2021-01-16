DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3"}}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SECRET_KEY = "secrekey"

INSTALLED_APPS = ["phonenumber_field", "tests"]
