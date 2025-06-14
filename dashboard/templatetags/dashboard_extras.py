# DENTALCLINICSYSTEM/dashboard/templatetags/dashboard_extras.py

from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Allows accessing a dictionary item by a variable key in Django templates.
    Usage: {{ my_dictionary|get_item:my_key }}
    """
    return dictionary.get(key)