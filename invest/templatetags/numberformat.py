from django import template

register = template.Library()

@register.filter(name='currency')
def currency(value, arg):
    str_val = f'{arg} {value:_.2f}'
    return str_val.replace('.',',').replace('_','.')

@register.filter(name='number')
def number(value, arg):
    str_val = f'{value:_.{arg}f}'
    return str_val.replace('.',',').replace('_','.')
