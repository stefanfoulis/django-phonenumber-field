from django.contrib import admin
from .models import Country, CallingCode

class CallingCodeInline(admin.TabularInline):
    model = CallingCode

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    inlines = (CallingCodeInline,)
