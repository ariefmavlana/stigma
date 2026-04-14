from django import template
from django.utils.safestring import mark_safe
import markdown as md

register = template.Library()


@register.filter
def reading_time_display(minutes):
    """Format reading time as a readable string."""
    if minutes < 1:
        return "< 1 min read"
    return f"{minutes} min read"


@register.filter
def render_markdown(value):
    """Render a markdown string to safe HTML."""
    if not value:
        return ""
    extensions = ["extra", "codehilite", "toc", "nl2br"]
    return mark_safe(md.markdown(value, extensions=extensions))


@register.simple_tag(takes_context=True)
def active_nav(context, url_name):
    """Return 'active' CSS class if the current URL matches the given name."""
    request = context.get("request")
    if request and request.resolver_match:
        if request.resolver_match.url_name == url_name:
            return "active"
    return ""
