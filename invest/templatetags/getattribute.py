# import re

from django import template
# from django.conf import settings

register = template.Library()

@register.filter(name='getattribute')
def getattribute(value, arg):
    '''Gets an attribute of an object dynamically from a string name'''
    if isinstance(value, dict):
        return value.get(arg)
    return getattr(value, arg)
