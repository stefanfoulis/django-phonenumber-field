from django.contrib import admin
from .models import Country, CountryCode

class CountryCodeInline(admin.TabularInline):
    model = CountryCode

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    inlines = (CountryCodeInline,)
