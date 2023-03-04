from django import template

register = template.Library()

@register.filter(name='currency')
def currency(value, arg):
    str_val = f'{arg} {value:_.2f}'
    return str_val.replace('.',',').replace('_','.')
