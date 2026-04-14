"""
Initial migration for the STIgma blog app.
Generated from blog/models.py.
"""

import uuid
import django.db.models.deletion
import django.utils.timezone
import markdownx.models
import taggit.managers
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("taggit", "0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
                ("slug", models.SlugField(blank=True, max_length=120, unique=True)),
                ("description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name_plural": "Categories",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Post",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=300)),
                ("slug", models.SlugField(blank=True, max_length=320, unique=True)),
                ("excerpt", models.TextField(blank=True, help_text="Short summary shown in listings. Leave blank to auto-generate.", max_length=500)),
                ("body", markdownx.models.MarkdownxField()),
                ("cover_image", models.ImageField(blank=True, null=True, upload_to="posts/covers/")),
                ("status", models.CharField(choices=[("draft", "Draft"), ("published", "Published"), ("archived", "Archived")], default="draft", max_length=20)),
                ("is_ai_generated", models.BooleanField(default=False, help_text="Was this post drafted with AI assistance?")),
                ("reading_time", models.PositiveSmallIntegerField(default=0, help_text="Estimated reading time in minutes.")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                ("views", models.PositiveIntegerField(default=0)),
                ("author", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="posts", to=settings.AUTH_USER_MODEL)),
                ("category", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="posts", to="blog.category")),
                ("tags", taggit.managers.TaggableManager(blank=True, help_text="A comma-separated list of tags.", through="taggit.TaggedItem", to="taggit.Tag", verbose_name="Tags")),
            ],
            options={
                "ordering": ["-published_at", "-created_at"],
                "indexes": [
                    models.Index(fields=["status", "published_at"], name="blog_post_status_pub_idx"),
                    models.Index(fields=["slug"], name="blog_post_slug_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="Comment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("author_name", models.CharField(max_length=100)),
                ("author_email", models.EmailField()),
                ("body", models.TextField(max_length=2000)),
                ("is_approved", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("post", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="comments", to="blog.post")),
            ],
            options={
                "ordering": ["created_at"],
            },
        ),
    ]
