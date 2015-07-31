from django.contrib import admin
from django.utils.encoding import force_text
from .models import Country, Code, CountryCode

class CountryCodeInline(admin.TabularInline):
    model = CountryCode

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "active", "codes")
    inlines = (CountryCodeInline,)
    extra = 0
    
    def codes(self, country):
        ids = list(country.country_codes.values_list("code__id", flat=True).distinct())
        ids.sort()
        return force_text(", ").join([force_text(i) for i in ids])

@admin.register(Code)
class CodeAdmin(admin.ModelAdmin):
    list_display = ("__unicode__", "active", "countries")
    inlines = (CountryCodeInline,)
    extra = 0
    
    def countries(self, code):
        names = list(code.country_codes.values_list("country__name", flat=True).distinct())
        names.sort()
        return force_text(", ").join(names)

@admin.register(CountryCode)
class CountryCodeAdmin(admin.ModelAdmin):
    list_display = ("get_country_id", "get_country_name", "get_code_id", "get_country_active", "get_code_active", "active", "all_active")
    
    def get_country_id(self, country_code):
        return country_code.country.id
    get_country_id.short_description = "Country ID"
    get_country_id.admin_order_field = "country__id"
    
    def get_country_name(self, country_code):
        return country_code.country.name
    get_country_name.short_description = "Country Name"
    get_country_name.admin_order_field = "country__name"
    
    def get_country_active(self, country_code):
        if country_code.country.active:
            html = '<img src="/static/admin/img/icon-yes.gif" alt="True" />'
        else:
            html = '<img src="/static/admin/img/icon-no.gif" alt="False" />'
        return html
    get_country_active.short_description = "Country Active"
    get_country_active.admin_order_field = "country__active"
    get_country_active.allow_tags = True
    
    def get_code_id(self, country_code):
        return country_code.code.id
    get_code_id.short_description = "Code ID"
    get_code_id.admin_order_field = "code__id"
    
    def get_code_active(self, country_code):
        if country_code.code.active:
            html = '<img src="/static/admin/img/icon-yes.gif" alt="True" />'
        else:
            html = '<img src="/static/admin/img/icon-no.gif" alt="False" />'
        return html
    get_code_active.short_description = "Code Active"
    get_code_active.admin_order_field = "code__active"
    get_code_active.allow_tags = True
    
    def all_active(self, country_code):
        if country_code.active and country_code.country.active and country_code.code.active:
            html = '<img src="/static/admin/img/icon-yes.gif" alt="True" />'
        else:
            html = '<img src="/static/admin/img/icon-no.gif" alt="False" />'
        return html
    all_active.allow_tags = True