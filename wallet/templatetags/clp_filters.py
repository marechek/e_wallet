from django import template

register = template.Library()


@register.filter
def clp(value):
    try:
        value = int(value)
        return f"${value:,.0f}".replace(",", ".")
    except:
        return value