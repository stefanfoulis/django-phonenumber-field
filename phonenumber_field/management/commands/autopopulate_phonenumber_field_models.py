from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.utils.encoding import force_text
from phonenumbers.data import _AVAILABLE_REGION_CODES, _COUNTRY_CODE_TO_REGION_CODE
from ...models import RegionCode, CallingCode, CountryCode

def clean_and_save(instance, added_list, errors_list):
    try:
        instance.full_clean()
    except ValidationError, e:
        errors_list.append([instance, e])
    else:
        instance.save()
        added_list.append(instance)

class Command(BaseCommand):
    def report_results(self, action, instances):
        if instances:
            len_instances = len(instances)
            width = len(force_text(len_instances))
            
            if len_instances == 1:
                name = instances[0]._meta.verbose_name
            else:
                name = instances[0]._meta.verbose_name_plural
            
            self.stdout.write("")
            self.stdout.write("%s the following %s:" % (action, name))
            for i, instance in enumerate(instances, start=1):
                self.stdout.write(force_text("\t{}) {}").format(force_text(i).zfill(width), instance))
            self.stdout.write("")
    
    def report_add_errors(self, instances):
        self.report_results("Failed to add", instances)
    
    def report_deactivations(self, instances):
        self.report_results("Deactivated", instances)
    
    def report_additions(self, instances):
        self.report_results("Added", instances)

    def handle(self, *args, **options):
        self.stdout.write("Adding region codes.")
        
        region_codes_added = []
        region_codes_add_errors = []
        for region_code in _AVAILABLE_REGION_CODES:
            try:
                instance = RegionCode.objects.get(code=region_code)
            except RegionCode.DoesNotExist:
                instance = RegionCode()
                instance.code = region_code
                instance.active = True
                clean_and_save(instance, region_codes_added, region_codes_add_errors)
        
        self.stdout.write("Deactivating region codes.")
        
        region_codes_deactivated = []
        for instance in RegionCode.objects.exclude(code__in=_AVAILABLE_REGION_CODES):
            instance.active = False
            instance.save()
            region_codes_deactivated.append(instance)
        
        self.stdout.write("Adding calling codes.")
        
        calling_codes_added = []
        calling_codes_add_errors = []
        for calling_code in _COUNTRY_CODE_TO_REGION_CODE.iterkeys():
            try:
                instance = CallingCode.objects.get(code=calling_code)
            except CallingCode.DoesNotExist:
                instance = CallingCode()
                instance.code = calling_code
                instance.active = True
                clean_and_save(instance, calling_codes_added, calling_codes_add_errors)
        
        self.stdout.write("Deactivating calling codes.")
        
        calling_codes_deactivated = []
        for instance in CallingCode.objects.exclude(code__in=_COUNTRY_CODE_TO_REGION_CODE.iterkeys()):
            instance.active = False
            instance.save()
            calling_codes_deactivated.append(instance)
        
        self.stdout.write("Adding country codes.")
        
        region_to_calling_code_map = {}
        for calling_code, region_codes in _COUNTRY_CODE_TO_REGION_CODE.iteritems():
            for region_code in region_codes:
                if region_code not in region_to_calling_code_map:
                    region_to_calling_code_map[region_code] = []
                region_to_calling_code_map[region_code].append(calling_code)
        
        country_codes_added = []
        country_codes_add_errors = []
        for region_code, calling_codes in region_to_calling_code_map.iteritems():
            try:
                region_code_obj = RegionCode.objects.get(code=region_code)
            except RegionCode.DoesNotExist:
                region_code_obj = None
            
            for calling_code in calling_codes:
                try:
                    calling_code_obj = CallingCode.objects.get(code=calling_code)
                except CallingCode.DoesNotExist:
                    calling_code_obj = None
                
                if calling_code_obj:
                    try:
                        instance = CountryCode.objects.get(region_code_obj=region_code_obj, calling_code_obj=calling_code_obj)
                    except CountryCode.DoesNotExist:
                        instance = CountryCode()
                        instance.region_code_obj = region_code_obj
                        instance.calling_code_obj = calling_code_obj
                        instance.active = True
                        clean_and_save(instance, country_codes_added, country_codes_add_errors)
        
        for iterable in (region_codes_added, calling_codes_added, country_codes_added):
            self.report_additions(iterable)
        
        for iterable in (region_codes_deactivated, calling_codes_deactivated):
            self.report_deactivations(iterable)
        
        for iterable in (region_codes_add_errors, calling_codes_add_errors, country_codes_add_errors):
            self.report_add_errors(iterable)
