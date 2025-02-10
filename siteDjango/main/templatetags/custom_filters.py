from django import template

register = template.Library()

@register.filter(name='sub')
def sub(value, arg):
    """Subtrai arg de value."""
    return value - arg

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)