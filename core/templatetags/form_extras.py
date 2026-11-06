from django import template

register = template.Library()


@register.filter
def add_class(field, css_class):
    """Render a bound form field with extra CSS classes appended to its widget."""
    attrs = field.field.widget.attrs
    existing = attrs.get("class", "")
    classes = f"{existing} {css_class}".strip()
    return field.as_widget(attrs={"class": classes})
