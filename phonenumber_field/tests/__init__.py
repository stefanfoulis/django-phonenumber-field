from django import VERSION

if VERSION < (1, 7):
    from .test_cases import *