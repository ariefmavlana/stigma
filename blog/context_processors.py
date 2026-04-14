from django.conf import settings
from .models import Category


def global_context(request):
    """Inject global context into every template."""
    return {
        "BLOG_NAME": getattr(settings, "BLOG_NAME", "STIgma"),
        "BLOG_TAGLINE": getattr(settings, "BLOG_TAGLINE", "Thoughts, crafted."),
        "global_categories": Category.objects.all()[:8],
    }
