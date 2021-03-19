from datetime import datetime
from django import template
register = template.Library()


@register.filter
def convert_str_date(value):
    print(value)
    return str(datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ"))
