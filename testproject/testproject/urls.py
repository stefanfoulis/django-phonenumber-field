import django
GTE_DJANGO_1_8 = django.VERSION >= (1, 8)

if GTE_DJANGO_1_8:
    urlpatterns = []
else:
    from django.conf.urls import patterns
    urlpatterns = patterns('')
