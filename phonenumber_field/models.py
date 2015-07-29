#-*- coding: utf-8 -*-
import uuid
from django.db import models

class Country(models.Model):
    class Meta:
        ordering = ('name',)
    
    id = models.CharField(primary_key=True, max_length=255)
    name = models.CharField(max_length=50)
    active = models.BooleanField(default=False)
    
    def __unicode__(self):
        return u"({0}) {1}".format(self.id, self.name)

class CallingCode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    country = models.ForeignKey(Country, related_name="calling_codes")
    code = models.CharField(max_length=255)
    
    def __unicode__(self):
        return u"{0} {1}".format(self.code, self.country)