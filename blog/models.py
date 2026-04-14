"""
STIgma Blog Models
───────────────────
Core data models for the blog: Category, Post, Comment.
"""

import uuid
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase, GenericUUIDTaggedItemBase
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify


class Category(models.Model):
    """Post category / section of the blog."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:category", kwargs={"slug": self.slug})

    @property
    def post_count(self):
        return self.posts.filter(status=Post.Status.PUBLISHED).count()


class UUIDTaggedItem(GenericUUIDTaggedItemBase, TaggedItemBase):
    class Meta:
        verbose_name = "Tag Connection"
        verbose_name_plural = "Tag Connections"


class Post(models.Model):
    """A blog post — the central content unit."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    # Identity
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=320, unique=True, blank=True)

    # Authorship
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="posts"
    )

    # Content
    excerpt = models.TextField(
        max_length=500,
        blank=True,
        help_text="Short summary shown in listings. Leave blank to auto-generate.",
    )
    body = MarkdownxField()

    # Categorisation
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
    )
    tags = TaggableManager(through=UUIDTaggedItem, blank=True)

    # Media
    cover_image = models.ImageField(
        upload_to="posts/covers/", blank=True, null=True
    )

    # Metadata
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    is_ai_generated = models.BooleanField(
        default=False, help_text="Was this post drafted with AI assistance?"
    )
    reading_time = models.PositiveSmallIntegerField(
        default=0, help_text="Estimated reading time in minutes."
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    # Stats
    views = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["status", "published_at"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # Auto-calculate reading time (~200 words per minute)
        word_count = len(self.body.split()) if self.body else 0
        self.reading_time = max(1, round(word_count / 200))

        # Auto-excerpt
        if not self.excerpt and self.body:
            plain = self.body[:400].replace("#", "").replace("*", "").replace("`", "")
            self.excerpt = plain.strip()

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:post_detail", kwargs={"slug": self.slug})

    @property
    def formatted_body(self):
        """Return HTML-rendered markdown body."""
        return markdownify(self.body)

    @classmethod
    def published_posts(cls):
        """Return all published posts queryset."""
        return cls.objects.filter(status=cls.Status.PUBLISHED)


class Comment(models.Model):
    """Reader comment on a post."""

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    body = models.TextField(max_length=2000)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author_name} on {self.post.title[:40]}"
