from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return float(value) * int(arg)
    except Exception as e:
        return f"Error: {e}"
