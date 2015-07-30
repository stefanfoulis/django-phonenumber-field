from django.contrib import admin
from .models import Country, Code, CountryCode

class CountryCodeInline(admin.TabularInline):
    model = CountryCode

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "codes")
    inlines = (CountryCodeInline,)
    extra = 0
    
    def codes(self, country):
        ids = list(country.country_codes.values_list("code__id", flat=True).distinct())
        ids.sort()
        return unicode(", ").join([unicode(i) for i in ids])

@admin.register(Code)
class CodeAdmin(admin.ModelAdmin):
    list_display = ("__unicode__", "countries")
    inlines = (CountryCodeInline,)
    extra = 0
    
    def countries(self, code):
        names = list(code.country_codes.values_list("country__name", flat=True).distinct())
        names.sort()
        return unicode(", ").join(names)

@admin.register(CountryCode)
class CountryCodeAdmin(admin.ModelAdmin):
    list_display = ("get_country_id", "get_country_name", "get_code_id")
    
    def get_country_id(self, country_code):
        return country_code.country.id
    get_country_id.short_description = "Country ID"
    get_country_id.admin_order_field = "country__id"
    
    def get_country_name(self, country_code):
        return country_code.country.name
    get_country_name.short_description = "Country Name"
    get_country_name.admin_order_field = "country__name"
    
    def get_code_id(self, country_code):
        return country_code.code.id
    get_code_id.short_description = "Code ID"
    get_code_id.admin_order_field = "code__id"