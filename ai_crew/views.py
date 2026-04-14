"""
STIgma — AI Crew Django Views
───────────────────────────────
Async generation: POST returns a task_id immediately; the crew runs in a
background thread; the frontend polls /ai/generate/status/<task_id>/.
This prevents HTTP timeouts on long LLM runs (2–5 minutes).
"""

import json
import logging
import re
import threading
import uuid as uuid_module

from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.db import close_old_connections

from blog.models import Post, Category
from .crew import BlogWriterCrew
from .forms import GeneratePostForm

logger = logging.getLogger(__name__)

# ── In-memory task store ──────────────────────────────────────────────────────
_tasks: dict = {}
_tasks_lock = threading.Lock()


def _clean_json(raw: str) -> str:
    """Strip markdown fences and leading prose — return only the JSON object."""
    raw = raw.strip()
    raw = re.sub(r"^```[a-zA-Z]*\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        raw = raw[start : end + 1]
    return raw.strip()


def _run_crew_background(task_id, topic, target_audience, tone, category_id, user_id):
    """
    Daemon thread: run the BlogWriterCrew, parse JSON, save a draft Post,
    and update the shared task store.
    """
    close_old_connections()
    try:
        from django.contrib.auth.models import User

        user = User.objects.get(pk=user_id)

        result = BlogWriterCrew().crew().kickoff(
            inputs={
                "topic": topic,
                "target_audience": target_audience,
                "tone": tone,
            }
        )

        raw = _clean_json(result.raw)
        post_data = json.loads(raw)

        post = Post(
            title=post_data.get("title", topic)[:300],
            excerpt=post_data.get("excerpt", "")[:500],
            body=post_data.get("body", raw),
            status=Post.Status.DRAFT,
            is_ai_generated=True,
            author=user,
            published_at=timezone.now(),
        )

        try:
            ai_rt = int(post_data.get("reading_time_minutes", 0))
            if ai_rt > 0:
                post.reading_time = ai_rt
        except (ValueError, TypeError):
            pass

        if category_id:
            try:
                post.category = Category.objects.get(pk=category_id)
            except Category.DoesNotExist:
                pass

        post.save()

        raw_tags = post_data.get("tags", [])
        if isinstance(raw_tags, list) and raw_tags:
            clean_tags = [str(t).strip()[:100] for t in raw_tags if t][:10]
            if clean_tags:
                post.tags.add(*clean_tags)

        with _tasks_lock:
            _tasks[task_id] = {
                "status": "done",
                "post_id": str(post.pk),
                "post_title": post.title,
                "post_admin_url": f"/admin/blog/post/{post.pk}/change/",
                "post_public_url": post.get_absolute_url(),
                "excerpt": (post.excerpt or "")[:280],
                "tags": list(post.tags.names()),
                "reading_time": post.reading_time,
            }
        logger.info("CrewAI task %s complete → Post pk=%s", task_id, post.pk)

    except json.JSONDecodeError as exc:
        logger.error("CrewAI output not valid JSON [task=%s]: %s", task_id, exc)
        with _tasks_lock:
            _tasks[task_id] = {
                "status": "error",
                "error": "The AI returned output that could not be parsed. Please try again.",
            }
    except Exception as exc:
        logger.exception("Background crew error [task=%s]", task_id)
        with _tasks_lock:
            _tasks[task_id] = {"status": "error", "error": str(exc)}
    finally:
        close_old_connections()


@staff_member_required
def generate_view(request):
    """
    GET  — Render generation form with recent AI posts.
    POST — Validate, start background thread, return {task_id} JSON.
    """
    recent_ai_posts = (
        Post.objects.filter(is_ai_generated=True)
        .select_related("author", "category")
        .order_by("-created_at")[:6]
    )

    if request.method == "POST":
        form = GeneratePostForm(request.POST)
        if not form.is_valid():
            return JsonResponse(
                {"error": "Form validation failed.", "field_errors": form.errors},
                status=400,
            )

        task_id = str(uuid_module.uuid4())
        topic = form.cleaned_data["topic"]
        cat_obj = form.cleaned_data.get("category")

        with _tasks_lock:
            _tasks[task_id] = {"status": "running", "topic": topic}

        thread = threading.Thread(
            target=_run_crew_background,
            args=(
                task_id,
                topic,
                form.cleaned_data["target_audience"],
                form.cleaned_data["tone"],
                cat_obj.pk if cat_obj else None,
                request.user.pk,
            ),
            daemon=True,
        )
        thread.start()
        logger.info("Started crew thread [task=%s, topic=%r]", task_id, topic)
        return JsonResponse({"task_id": task_id, "status": "running"})

    form = GeneratePostForm()
    return render(
        request,
        "ai_crew/generate.html",
        {
            "form": form,
            "title": "AI Post Generator",
            "recent_ai_posts": recent_ai_posts,
        },
    )


@staff_member_required
@require_http_methods(["GET"])
def task_status_view(request, task_id):
    """Poll endpoint — returns current task state as JSON."""
    with _tasks_lock:
        task = _tasks.get(task_id)
    if task is None:
        return JsonResponse({"status": "not_found"}, status=404)
    return JsonResponse(task)
