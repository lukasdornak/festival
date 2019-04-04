import re
from django import template


register = template.Library()


@register.filter(name='add_nbsps')
def add_nbsps(value):
    return re.sub(r'([\>\s;][aikosuvzAIKOSUVZ])(\s)', r"\1&nbsp;", value)