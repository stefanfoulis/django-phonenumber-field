from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.utils.encoding import force_text
from phonenumbers.data import _COUNTRY_CODE_TO_REGION_CODE
from django_countries.data import COUNTRIES
from ...models import Country, Code, CountryCode

class Command(BaseCommand):

    def handle(self, *args, **options):
        #
        #    query database for current countries
        #
        self.stdout.write("Building a list of countries currently stored in the database.")
        
        old_dict = {}
        for country in Country.objects.all():
            old_dict[country.id] = {"name":country.name, "active": country.active}
        
        #
        #    build comparison map
        #
        self.stdout.write("Building a list of countries for comparison.")
        
        new_dict = {}
        for country_id, country_name in COUNTRIES.iteritems():
            if country_id in new_dict:
                continue
            new_dict[country_id] = {"name":country_name[:50], "active": True}
        
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
        deactivated_country_count = Country.objects.filter(id__in=removed_keys, active=True).update(active=False)
        
        # adjust unchanged_count
        unchanged_count += removed_count - deactivated_country_count
        
        # add new countries
        failed_to_add = []
        for key in added_keys:
            fields = {
                "id": key,
                "name": new_dict[key]["name"],
                "active": True,
            }
            country = Country(**fields)
            
            try:
                country.full_clean()
            except ValidationError, e:
                failed_to_add.append([fields, e])
            else:
                country.save()
        
        if failed_to_add:
            self.stdout.write("")
            self.stdout.write("Failed to add the following countries:")
            for record in failed_to_add:
                self.stdout.write(force_text(record))
            self.stdout.write("")
        
        # change existing keys
        failed_to_change = []
        for key in changed_keys:
            country = Country.objects.get(id=key)
            country.name = new_dict[key]["name"]
            country.active = True
        
            try:
                country.full_clean()
            except ValidationError, e:
                d = {}
                for k in ("id", "name", "active"):
                    d[k] = getattr(country, k)
                failed_to_change.append([d, e])
            else:
                country.save()
        
        if failed_to_change:
            self.stdout.write("")
            self.stdout.write("Failed to change the following countries:")
            for record in failed_to_change:
                self.stdout.write(force_text(record))
            self.stdout.write("")
        
        #
        #    announce
        #
        self.stdout.write("")
        self.stdout.write("-------------------------------")
        self.stdout.write("-------------------------------")
        self.stdout.write("------ COUNTRIES SUMMARY ------")
        self.stdout.write("-------------------------------")
        self.stdout.write("-------------------------------")
        self.stdout.write("There are %d records total." % len(old_dict))
        self.stdout.write("Deactivated %d countries." % deactivated_country_count)
        self.stdout.write("Added %d countries." % (len(added_keys) - len(failed_to_add)))
        self.stdout.write("Failed to add %d countries." % len(failed_to_add))
        self.stdout.write("Changed %d countries." % (len(changed_keys) - len(failed_to_change)))
        self.stdout.write("Failed to change %d countries." % len(failed_to_change))
        self.stdout.write("%d countries are unchanged." % (unchanged_count + len(failed_to_change)))
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
        
        for country_code, calling_codes in country_calling_codes.iteritems():
            try:
                country = Country.objects.get(id=country_code)
            except Country.DoesNotExist:
                country = None
            
            for calling_code in calling_codes:
                try:
                    code = Code.objects.get(id=calling_code)
                except Code.DoesNotExist:
                    code = Code()
                    code.id = calling_code
                    code.active = True
                    
                    try:
                        code.full_clean()
                    except ValidationError, e:
                        d = {}
                        for k in ("id", "active"):
                            d[k] = getattr(code, k)
                        failed_to_add_code.append([d, e])
                        continue
                    else:
                        code.save()
                        added_code += 1
                
                if country:
                    try:
                        country_code = CountryCode.objects.get(country=country, code=code)
                    except CountryCode.DoesNotExist:
                        country_code = CountryCode(country=country, code=code, active=True)
                        
                        try:
                            country_code.full_clean()
                        except ValidationError, e:
                            d = {}
                            for k in ("country", "code", "active"):
                                d[k] = getattr(country_code, k)
                            failed_to_add_country_code.append([d, e])
                        else:
                            country_code.save()
                            added_country_code += 1
                    
        
        if failed_to_add_code:
            self.stdout.write("")
            self.stdout.write("Failed to add the following codes:")
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
        self.stdout.write("---------------------------")
        self.stdout.write("---------------------------")
        self.stdout.write("------ CODES SUMMARY ------")
        self.stdout.write("---------------------------")
        self.stdout.write("---------------------------")
        self.stdout.write("Added %d codes." % added_code)
        self.stdout.write("Failed to add %d codes." % len(failed_to_add_code))
        self.stdout.write("Added %d country codes." % added_country_code)
        self.stdout.write("Failed to add %d country codes." % len(failed_to_add_country_code))
        self.stdout.write("")