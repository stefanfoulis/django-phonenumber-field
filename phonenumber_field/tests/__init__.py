from django import VERSION

if VERSION < (1, 6):
    from .test_cases import *
