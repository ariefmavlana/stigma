"""
STIgma Blog Admin
──────────────────
Monochrome-friendly admin registration for Post, Category, Comment.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.timezone import now
from markdownx.admin import MarkdownxModelAdmin
from .models import Post, Category, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ["name", "slug", "post_count", "created_at"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "description"]
    ordering      = ["name"]


@admin.register(Post)
class PostAdmin(MarkdownxModelAdmin):
    list_display = [
        "title",
        "author",
        "category",
        "status_badge",
        "ai_badge",
        "reading_time_display",
        "views",
        "published_at",
    ]
    list_filter      = ["status", "is_ai_generated", "category", "created_at"]
    search_fields    = ["title", "body", "excerpt"]
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy   = "created_at"
    ordering         = ["-created_at"]
    readonly_fields  = ["views", "reading_time", "created_at", "updated_at"]
    list_per_page    = 25
    save_on_top      = True

    fieldsets = (
        (
            "Content",
            {"fields": ("title", "slug", "excerpt", "body", "cover_image")},
        ),
        (
            "Classification",
            {"fields": ("category", "tags")},
        ),
        (
            "Publication",
            {"fields": ("status", "author", "published_at", "is_ai_generated")},
        ),
        (
            "Statistics",
            {
                "fields": ("views", "reading_time", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def status_badge(self, obj):
        styles = {
            "published": "color:#166534; border:1px solid #bbf7d0; background:#f0fdf4; padding:2px 7px; font-size:0.7rem; letter-spacing:0.08em; text-transform:uppercase; font-family:monospace;",
            "draft":     "color:#374151; border:1px solid #d1d5db; background:#f9fafb; padding:2px 7px; font-size:0.7rem; letter-spacing:0.08em; text-transform:uppercase; font-family:monospace;",
            "archived":  "color:#991b1b; border:1px solid #fecaca; background:#fef2f2; padding:2px 7px; font-size:0.7rem; letter-spacing:0.08em; text-transform:uppercase; font-family:monospace;",
        }
        style = styles.get(obj.status, styles["draft"])
        return format_html('<span style="{}">{}</span>', style, obj.get_status_display())
    status_badge.short_description = "Status"
    status_badge.admin_order_field = "status"

    def ai_badge(self, obj):
        if obj.is_ai_generated:
            return format_html(
                '<span style="color:#6b7280; font-family:monospace; font-size:0.7rem;">✦ AI</span>'
            )
        return format_html('<span style="color:#d1d5db; font-size:0.75rem;">—</span>')
    ai_badge.short_description = "AI"
    ai_badge.admin_order_field = "is_ai_generated"

    def reading_time_display(self, obj):
        return format_html(
            '<span style="font-family:monospace; font-size:0.8rem; color:#6b7280;">{} min</span>',
            obj.reading_time,
        )
    reading_time_display.short_description = "Read"
    reading_time_display.admin_order_field = "reading_time"

    actions = ["publish_posts", "draft_posts"]

    @admin.action(description="Publish selected posts")
    def publish_posts(self, request, queryset):
        updated = queryset.update(status=Post.Status.PUBLISHED, published_at=now())
        self.message_user(request, f"{updated} post(s) published.")

    @admin.action(description="Revert selected posts to Draft")
    def draft_posts(self, request, queryset):
        updated = queryset.update(status=Post.Status.DRAFT)
        self.message_user(request, f"{updated} post(s) moved to Draft.")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display  = ["author_name", "post", "approved_badge", "created_at"]
    list_filter   = ["is_approved", "created_at"]
    search_fields = ["author_name", "body", "post__title"]
    readonly_fields = ["created_at"]
    actions       = ["approve_comments", "unapprove_comments"]

    def approved_badge(self, obj):
        if obj.is_approved:
            return format_html(
                '<span style="font-family:monospace; font-size:0.7rem; color:#166534;">✓ Approved</span>'
            )
        return format_html(
            '<span style="font-family:monospace; font-size:0.7rem; color:#92400e;">Pending</span>'
        )
    approved_badge.short_description = "Status"
    approved_badge.admin_order_field = "is_approved"

    @admin.action(description="Approve selected comments")
    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} comment(s) approved.")

    @admin.action(description="Unapprove selected comments")
    def unapprove_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f"{updated} comment(s) unapproved.")
