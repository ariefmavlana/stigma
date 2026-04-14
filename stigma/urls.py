from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# ── Admin site branding ───────────────────────────────────────────────────────
admin.site.site_header = getattr(settings, "ADMIN_SITE_HEADER", "✦ STIgma Admin")
admin.site.site_title  = getattr(settings, "ADMIN_SITE_TITLE",  "STIgma")
admin.site.index_title = getattr(settings, "ADMIN_INDEX_TITLE", "Dashboard")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("markdownx/", include("markdownx.urls")),
    path("ai/", include("ai_crew.urls", namespace="ai_crew")),
    path("", include("blog.urls", namespace="blog")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
