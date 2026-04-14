"""
STIgma Blog Views
──────────────────
Public-facing blog pages: home, post detail, category/tag listings, search.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.db.models import Q, F
from django.conf import settings
from django.utils import timezone

from .models import Post, Category, Comment
from .forms import CommentForm


def home(request):
    """Homepage — featured post + recent posts grid."""
    published = (
        Post.objects.filter(status=Post.Status.PUBLISHED)
        .select_related("author", "category")
        .prefetch_related("tags")
    )

    featured = published.first()

    # Safely exclude featured from recents (featured may be None)
    if featured:
        recent = published.exclude(pk=featured.pk)[:8]
    else:
        recent = published[:8]

    categories = Category.objects.all()[:6]

    return render(
        request,
        "blog/home.html",
        {
            "featured": featured,
            "recent_posts": recent,
            "categories": categories,
        },
    )


def post_list(request):
    """Full paginated post listing."""
    published = (
        Post.objects.filter(status=Post.Status.PUBLISHED)
        .select_related("author", "category")
        .prefetch_related("tags")
    )

    paginator = Paginator(published, settings.BLOG_POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return render(request, "blog/post_list.html", {"page": page})


def post_detail(request, slug):
    """Individual post view with comment form."""
    post = get_object_or_404(Post, slug=slug, status=Post.Status.PUBLISHED)

    # Atomic view-count increment (no race condition)
    Post.objects.filter(pk=post.pk).update(views=F("views") + 1)

    approved_comments = post.comments.filter(is_approved=True)
    comment_form = CommentForm()

    # Related posts: same category, excluding self
    related = (
        Post.objects.filter(status=Post.Status.PUBLISHED, category=post.category)
        .exclude(pk=post.pk)
        .select_related("author")[:3]
        if post.category
        else Post.objects.none()
    )

    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
            messages.success(
                request,
                "Your comment has been submitted and is awaiting approval. Thank you!",
            )
            return redirect(post.get_absolute_url())

    return render(
        request,
        "blog/post_detail.html",
        {
            "post": post,
            "comments": approved_comments,
            "comment_form": comment_form,
            "related_posts": related,
        },
    )


def category_detail(request, slug):
    """Posts filtered by category."""
    category = get_object_or_404(Category, slug=slug)
    posts = (
        Post.objects.filter(status=Post.Status.PUBLISHED, category=category)
        .select_related("author")
    )

    paginator = Paginator(posts, settings.BLOG_POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return render(
        request,
        "blog/category_detail.html",
        {"category": category, "page": page},
    )


def tag_detail(request, slug):
    """Posts filtered by tag."""
    from taggit.models import Tag

    tag = get_object_or_404(Tag, slug=slug)
    posts = (
        Post.objects.filter(status=Post.Status.PUBLISHED, tags__slug=slug)
        .select_related("author", "category")
        .distinct()
    )

    paginator = Paginator(posts, settings.BLOG_POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return render(
        request,
        "blog/tag_detail.html",
        {"tag": tag, "page": page},
    )


def search(request):
    """Full-text search across post titles and bodies."""
    query = request.GET.get("q", "").strip()
    results = Post.objects.none()

    if query:
        results = (
            Post.objects.filter(status=Post.Status.PUBLISHED)
            .filter(
                Q(title__icontains=query)
                | Q(body__icontains=query)
                | Q(excerpt__icontains=query)
            )
            .select_related("author", "category")
            .distinct()
        )

    return render(
        request,
        "blog/search.html",
        {"query": query, "results": results},
    )


def about(request):
    """About page."""
    return render(request, "blog/about.html")
