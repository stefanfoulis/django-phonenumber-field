#-*- coding: utf-8 -*-
from babel import Locale
from django.core import validators
from django.core.cache import caches, DEFAULT_CACHE_ALIAS
from django.db import models
from django.db.models.signals import post_save
from django.utils.encoding import force_text
from django.utils.functional import cached_property
from django.utils import translation
from uuid import uuid4
from .fields.models.caseinsensitivecharfield import CaseInsensitiveCharField

cache = caches[DEFAULT_CACHE_ALIAS]

class RegionCode(models.Model):
    class Meta:
        ordering = ("code",)
    
    code = CaseInsensitiveCharField(primary_key=True, max_length=2)
    active = models.BooleanField(default=False)
    
    def __unicode__(self):
        if translation.get_language():
            return force_text("{} ({})").format(self.name, self.code)
        return self.code
    
    @cached_property
    def name(self):
        if translation.get_language():
            locale = Locale(translation.to_locale(translation.get_language()))
            return locale.territories.get(self.code)
        return self.code

class CallingCode(models.Model):
    class Meta:
        ordering = ("code",)
    
    code = models.PositiveSmallIntegerField(primary_key=True, validators=[validators.MinValueValidator(1)])
    active = models.BooleanField(default=False)
    
    def __unicode__(self):
        return force_text(self.code)

class CountryCodeManager(models.Manager):
    def get_by_natural_key(self, region_code, calling_code):
        kwargs = {"calling_code_obj__code": calling_code}
        if region_code is None:
            kwargs["region_code_obj__isnull"] = True
        else:
            kwargs["region_code_obj__code"] = region_code
        return CountryCode.objects.get(**kwargs)

class CountryCode(models.Model):
    class Meta:
        unique_together = ("region_code_obj", "calling_code_obj")
        ordering = unique_together
    
    objects = CountryCodeManager()
    
    region_code_obj = models.OneToOneField(RegionCode, related_name="country_code", null=True, blank=True)
    calling_code_obj = models.ForeignKey(CallingCode, related_name="country_codes")
    active = models.BooleanField(default=False)
    
    def __unicode__(self):
        fmt_str = force_text("+{}")
        fmt_args = [self.calling_code_obj]
        if self.region_code_obj:
            fmt_str = force_text("{}, %s") % fmt_str
            fmt_args.insert(0, self.region_code_obj)
        return fmt_str.format(*fmt_args)
    
    def natural_key(self):
        return (self.region_code, self.calling_code)
    
    @cached_property
    def calling_code(self):
        return self.calling_code_obj.code
    
    @cached_property
    def region_code(self):
        return self.region_code_obj.code if self.region_code_obj else None

CACHE_BUSTER_KEY = ".".join(("django", __name__, "CACHE_BUSTER_KEY"))

def set_cache_buster(**kwargs):
    buster = uuid4().hex
    cache.set(CACHE_BUSTER_KEY, buster, None)
    return buster

def get_cache_buster():
    buster = cache.get(CACHE_BUSTER_KEY)
    if buster is None:
        buster = set_cache_buster()
    return buster

for cls in (RegionCode, CallingCode, CountryCode):
    post_save.connect(set_cache_buster, sender=cls)