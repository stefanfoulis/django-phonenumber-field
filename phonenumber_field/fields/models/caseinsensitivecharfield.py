from django.db import models

class CaseInsensitiveCharField(models.CharField):
    def db_type(self, connection):
        return "varchar(%d) collate nocase" % self.max_length