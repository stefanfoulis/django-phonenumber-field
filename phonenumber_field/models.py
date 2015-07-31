#-*- coding: utf-8 -*-
from babel import Locale
from django.db import models
from django.core import validators
from django.utils.encoding import force_text
from django.utils.functional import cached_property
from django.utils import translation
from .fields.models.caseinsensitivecharfield import CaseInsensitiveCharField

class RegionCode(models.Model):
    class Meta:
        ordering = ("code",)
    
    code = CaseInsensitiveCharField(primary_key=True, max_length=2)
    active = models.BooleanField(default=False)
    
    def __unicode__(self):
        return force_text("{} ({})").format(self.name, self.code)
    
    @cached_property
    def name(self):
        locale = Locale(translation.to_locale(translation.get_language()))
        return locale.territories.get(self.code)

class CallingCode(models.Model):
    class Meta:
        ordering = ("code",)
    
    code = models.PositiveSmallIntegerField(primary_key=True, validators=[validators.MinValueValidator(1)])
    active = models.BooleanField(default=False)
    
    def __unicode__(self):
        return force_text(self.code)

class CountryCodeManager(models.Manager):
    def get_by_natural_key(self, country, code):
        return self.get(country=country, code=code)

class CountryCode(models.Model):
    class Meta:
        unique_together = ("region_code_obj", "calling_code_obj")
        ordering = unique_together
    
    objects = CountryCodeManager()
    
    region_code_obj = models.OneToOneField(RegionCode, related_name="country_code", null=True, blank=True)
    calling_code_obj = models.ForeignKey(CallingCode, related_name="country_codes")
    active = models.BooleanField(default=False)
    
    def __unicode__(self):
        return force_text("{}, +{}").format(self.region_code_obj, self.calling_code_obj)
    
    @cached_property
    def calling_code(self):
        return self.calling_code_obj.code
    
    @cached_property
    def region_code(self):
        return self.region_code_obj.code if self.region_code_obj else None
