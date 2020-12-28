from django import template

register = template.Library()

@register.filter(name='range')
def filter_range(number):
    if number is not None:
        return range(number)
    else:
        return range(0)
