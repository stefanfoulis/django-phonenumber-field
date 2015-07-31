from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.utils.encoding import force_text
from phonenumbers.data import _COUNTRY_CODE_TO_REGION_CODE
from django_countries.data import COUNTRIES
from ...models import RegionCode, CallingCode, CountryCode

class Command(BaseCommand):

    def handle(self, *args, **options):
        #
        #    query database for current countries
        #
        self.stdout.write("Building a list of countries currently stored in the database.")
        
        old_dict = {}
        for region_code_obj in RegionCode.objects.all():
            old_dict[region_code_obj.code] = {"name":region_code_obj.name, "active": region_code_obj.active}
        
        #
        #    build comparison map
        #
        self.stdout.write("Building a list of countries for comparison.")
        
        new_dict = {}
        for region_code, country_name in COUNTRIES.iteritems():
            if region_code in new_dict:
                continue
            new_dict[region_code] = {"name":country_name[:50], "active": True}
        
        #
        #    compare
        #
        self.stdout.write("Comparing these lists.")
        
        old_keys, new_keys = [
            set(d.keys()) for d in (old_dict, new_dict)
        ]
        
        intersect_keys = new_keys.intersection(old_keys)
        
        removed_keys = old_keys - intersect_keys
        removed_count = len(removed_keys)
        added_keys = new_keys - intersect_keys
        changed_keys = set(c for c in intersect_keys if old_dict[c] != new_dict[c])
        unchanged_keys = intersect_keys - changed_keys
        unchanged_count = len(unchanged_keys)
        
        #
        #    persist changes
        #
        self.stdout.write("Committing changes to database.")
        
        # deactivate removed countries
        deactivated_country_count = RegionCode.objects.filter(code__in=removed_keys, active=True).update(active=False)
        
        # adjust unchanged_count
        unchanged_count += removed_count - deactivated_country_count
        
        # add new countries
        failed_to_add = []
        for key in added_keys:
            fields = {
                "code": key,
                "name": new_dict[key]["name"],
                "active": True,
            }
            region_code_obj = RegionCode(**fields)
            
            try:
                region_code_obj.full_clean()
            except ValidationError, e:
                failed_to_add.append([fields, e])
            else:
                region_code_obj.save()
        
        if failed_to_add:
            self.stdout.write("")
            self.stdout.write("Failed to add the following region codes:")
            for record in failed_to_add:
                self.stdout.write(force_text(record))
            self.stdout.write("")
        
        # change existing keys
        failed_to_change = []
        for key in changed_keys:
            region_code_obj = RegionCode.objects.get(code=key)
            region_code_obj.name = new_dict[key]["name"]
            region_code_obj.active = True
        
            try:
                region_code_obj.full_clean()
            except ValidationError, e:
                d = {}
                for k in ("code", "name", "active"):
                    d[k] = getattr(region_code_obj, k)
                failed_to_change.append([d, e])
            else:
                region_code_obj.save()
        
        if failed_to_change:
            self.stdout.write("")
            self.stdout.write("Failed to change the following region codes:")
            for record in failed_to_change:
                self.stdout.write(force_text(record))
            self.stdout.write("")
        
        #
        #    announce
        #
        self.stdout.write("")
        self.stdout.write("---------------------------------")
        self.stdout.write("---------------------------------")
        self.stdout.write("------ REGION CODE SUMMARY ------")
        self.stdout.write("---------------------------------")
        self.stdout.write("---------------------------------")
        self.stdout.write("There are %d records total." % len(old_dict))
        self.stdout.write("Deactivated %d region codes." % deactivated_country_count)
        self.stdout.write("Added %d region codes." % (len(added_keys) - len(failed_to_add)))
        self.stdout.write("Failed to add %d region codes." % len(failed_to_add))
        self.stdout.write("Changed %d region codes." % (len(changed_keys) - len(failed_to_change)))
        self.stdout.write("Failed to change %d region codes." % len(failed_to_change))
        self.stdout.write("%d region codes are unchanged." % (unchanged_count + len(failed_to_change)))
        self.stdout.write("")
        
        #
        #    update calling codes
        #
        self.stdout.write("Updating calling codes.")
        
        country_calling_codes = {}
        failed_to_add_code = []
        failed_to_add_country_code = []
        added_code = 0
        added_country_code = 0
        for calling_code, country_codes in _COUNTRY_CODE_TO_REGION_CODE.iteritems():
            for country_code in country_codes:
                if country_code not in country_calling_codes:
                    country_calling_codes[country_code] = []
                country_calling_codes[country_code].append(calling_code)
        
        for region_code, calling_codes in country_calling_codes.iteritems():
            try:
                region_code_obj = RegionCode.objects.get(code=region_code)
            except RegionCode.DoesNotExist:
                region_code_obj = None
            
            for calling_code in calling_codes:
                try:
                    calling_code_obj = CallingCode.objects.get(code=calling_code)
                except CallingCode.DoesNotExist:
                    calling_code_obj = CallingCode()
                    calling_code_obj.code = calling_code
                    calling_code_obj.active = True
                    
                    try:
                        calling_code_obj.full_clean()
                    except ValidationError, e:
                        d = {}
                        for k in ("code", "active"):
                            d[k] = getattr(calling_code_obj, k)
                        failed_to_add_code.append([d, e])
                        continue
                    else:
                        calling_code_obj.save()
                        added_code += 1
                
                if calling_code_obj:
                    try:
                        country_code = CountryCode.objects.get(region_code_obj=region_code_obj, calling_code_obj=calling_code_obj)
                    except CountryCode.DoesNotExist:
                        country_code = CountryCode(region_code_obj=region_code_obj, calling_code_obj=calling_code_obj, active=True)
                        
                        try:
                            country_code.full_clean()
                        except ValidationError, e:
                            d = {}
                            for k in ("region_code_obj", "calling_code_obj", "active"):
                                d[k] = getattr(country_code, k)
                            failed_to_add_country_code.append([d, e])
                        else:
                            country_code.save()
                            added_country_code += 1
                    
        
        if failed_to_add_code:
            self.stdout.write("")
            self.stdout.write("Failed to add the following calling codes:")
            for record in failed_to_add_code:
                self.stdout.write(force_text(record))
            self.stdout.write("")
        
        if failed_to_add_country_code:
            self.stdout.write("")
            self.stdout.write("Failed to add the following country codes:")
            for record in failed_to_add_country_code:
                self.stdout.write(force_text(record))
            self.stdout.write("")
        
        self.stdout.write("")
        self.stdout.write("---------------------------------------------")
        self.stdout.write("---------------------------------------------")
        self.stdout.write("------ CALLING & COUNTRY CODES SUMMARY ------")
        self.stdout.write("---------------------------------------------")
        self.stdout.write("---------------------------------------------")
        self.stdout.write("Added %d calling codes." % added_code)
        self.stdout.write("Failed to add %d calling codes." % len(failed_to_add_code))
        self.stdout.write("Added %d country codes." % added_country_code)
        self.stdout.write("Failed to add %d country codes." % len(failed_to_add_country_code))
        self.stdout.write("")