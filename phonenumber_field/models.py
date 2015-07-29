#-*- coding: utf-8 -*-
from django.db import models
from .fields.models.caseinsensitivecharfield import CaseInsensitiveCharField

class Country(models.Model):
    id = CaseInsensitiveCharField(primary_key=True, max_length=2)
    name = models.CharField(max_length=50)
    active = models.BooleanField(default=False)
    
    def __unicode__(self):
        return unicode("({0}) {1}").format(self.id, self.name)

class Code(models.Model):
    id = CaseInsensitiveCharField(primary_key=True, max_length=3)
    active = models.BooleanField(default=False)
    
    def __unicode__(self):
        return unicode(self.id)

class CountryCodeManager(models.Manager):
    def get_by_natural_key(self, country, code):
        return self.get(country=country, code=code)

class CountryCode(models.Model):
    class Meta:
        unique_together = ("country", "code")
        ordering = unique_together
    
    objects = CountryCodeManager()
    
    country = models.ForeignKey(Country)
    code = models.ForeignKey(Code)
    
    def __unicode__(self):
        return unicode("{} {}").format(self.code, self.country)