from django import template

register = template.Library()

@register.filter(name='split_choices')
def split_choices(value):
    if value:
        return [choice.strip() for choice in value.split(',')]
    return []
