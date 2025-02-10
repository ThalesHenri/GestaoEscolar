from django import template

register = template.Library()

@register.filter(name='sub')
def sub(value, arg):
    """Subtrai arg de value."""
    return value - arg