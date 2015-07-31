from django.contrib import admin
from django.utils.encoding import force_text
from .models import RegionCode, CallingCode, CountryCode

class CountryCodeInline(admin.TabularInline):
    model = CountryCode

@admin.register(RegionCode)
class RegionCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "active", "calling_code")
    inlines = (CountryCodeInline,)
    extra = 0
    
    def calling_code(self, region_code):
        return region_code.country_code.calling_code

@admin.register(CallingCode)
class CallingCodeAdmin(admin.ModelAdmin):
    list_display = ("__unicode__", "active", "region_codes")
    inlines = (CountryCodeInline,)
    extra = 0
    
    def region_codes(self, calling_code):
        regions = [r for r in list(calling_code.country_codes.values_list("region_code_obj__code", flat=True).distinct()) if not r is None]
        if regions:
            regions.sort()
            regions = force_text(", ").join(regions)
        else:
            regions = None
        return regions

@admin.register(CountryCode)
class CountryCodeAdmin(admin.ModelAdmin):
    list_display = ("get_region_code", "get_calling_code", "get_region_code_active", "get_calling_code_active", "active", "all_active")
    
    def get_region_code(self, country_code):
        return country_code.region_code
    get_region_code.short_description = "Region Code"
    get_region_code.admin_order_field = "region_code_obj__code"
    
    def get_region_code_active(self, country_code):
        if country_code.region_code_obj and country_code.region_code_obj.active:
            html = '<img src="/static/admin/img/icon-yes.gif" alt="True" />'
        else:
            html = '<img src="/static/admin/img/icon-no.gif" alt="False" />'
        return html
    get_region_code_active.short_description = "Region Code Active"
    get_region_code_active.admin_order_field = "region_code_obj__active"
    get_region_code_active.allow_tags = True
    
    def get_calling_code(self, country_code):
        return country_code.calling_code
    get_calling_code.short_description = "Calling Code"
    get_calling_code.admin_order_field = "calling_code_obj__code"
    
    def get_calling_code_active(self, country_code):
        if country_code.calling_code_obj.active:
            html = '<img src="/static/admin/img/icon-yes.gif" alt="True" />'
        else:
            html = '<img src="/static/admin/img/icon-no.gif" alt="False" />'
        return html
    get_calling_code_active.short_description = "Code Active"
    get_calling_code_active.admin_order_field = "calling_code_obj__active"
    get_calling_code_active.allow_tags = True
    
    def all_active(self, country_code):
        if country_code.active and (not country_code.region_code_obj or country_code.region_code_obj.active) and country_code.calling_code_obj.active:
            html = '<img src="/static/admin/img/icon-yes.gif" alt="True" />'
        else:
            html = '<img src="/static/admin/img/icon-no.gif" alt="False" />'
        return html
    all_active.allow_tags = True