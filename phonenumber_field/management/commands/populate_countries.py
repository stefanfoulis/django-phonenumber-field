from django.core.management.base import BaseCommand
from phonenumbers.data import _COUNTRY_CODE_TO_REGION_CODE
from django_countries.data import COUNTRIES
from ...models import Country, CallingCode

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
            new_dict[country_id] = {"name":country_name, "active": True}
        
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
        Country.objects.bulk_create([
            Country(id=key, name=new_dict[key]["name"], active=True)
            for key in added_keys
        ])
        
        # change existing keys
        for key in changed_keys:
            Country.objects.filter(id=key).update(name=new_dict[key]["name"], active=True)
        
        #
        #    announce
        #
        self.stdout.write("")
        self.stdout.write("---------------------")
        self.stdout.write("---------------------")
        self.stdout.write("------ SUMMARY ------")
        self.stdout.write("---------------------")
        self.stdout.write("---------------------")
        self.stdout.write("There are %d records total." % len(old_dict))
        self.stdout.write("Deactivated shipping to %d countries." % deactivated_country_count)
        self.stdout.write("Added %d countries." % len(added_keys))
        self.stdout.write("Changed %d countries." % len(changed_keys))
        self.stdout.write("%d countries are unchanged." % unchanged_count)
        self.stdout.write("")
        
        #
        #    update calling codes
        #
        self.stdout.write("Updating calling codes.")
        
        country_calling_codes = {}
        for calling_code, country_codes in _COUNTRY_CODE_TO_REGION_CODE.iteritems():
            for country_code in country_codes:
                if country_code not in country_calling_codes:
                    country_calling_codes[country_code] = []
                country_calling_codes[country_code].append(calling_code)
        
        for country_code, calling_codes in country_calling_codes.iteritems():
            try:
                country = Country.objects.get(id=country_code)
            except Country.DoesNotExist:
                country = Country()
                country.id = country_code
                country.name = COUNTRIES[country_code] if country_code in COUNTRIES else country_code
                country.save()
            saved_calling_codes = [calling_code.code for calling_code in country.calling_codes.all()]
            for calling_code in calling_codes:
                if calling_code not in saved_calling_codes:
                    cc = CallingCode()
                    cc.country = country
                    cc.code = calling_code
                    cc.save()
