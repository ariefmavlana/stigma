"""
STIgma — AI Crew Django Views
───────────────────────────────
Async generation: Uses Celery + Redis to run the CrewAI pipeline.
The frontend polls /ai/generate/status/<task_id>/ which queries Celery.
"""

import logging
import time

from celery.result import AsyncResult
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods, require_POST

from blog.models import Post
from .forms import GeneratePostForm
from .tasks import generate_ai_post_task

logger = logging.getLogger(__name__)


@staff_member_required
def generate_view(request):
    """
    GET  — Render generation form with recent AI posts.
    POST — Dispatch Celery task, return {task_id}.
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

        topic = form.cleaned_data["topic"]
        cat_obj = form.cleaned_data.get("category")
        
        # Start time in MS for the Hyperscript timer
        start_time_ms = time.time() * 1000

        # Dispatch Celery task
        task = generate_ai_post_task.delay(
            topic=topic,
            target_audience=form.cleaned_data["target_audience"],
            tone=form.cleaned_data["tone"],
            language=form.cleaned_data.get("language", "Indonesian"),
            category_id=cat_obj.pk if cat_obj else None,
            user_id=request.user.pk,
            start_time=start_time_ms
        )
        
        task_id = task.id
        request.session['active_ai_task_id'] = task_id
        logger.info("Dispatched celery task [id=%s, topic=%r]", task_id, topic)
        
        if request.headers.get("HX-Request"):
            return render(request, "ai_crew/partials/status_running.html", {
                "task_id": task_id,
                "progress": 5,
                "start_time": start_time_ms
            })
            
        return JsonResponse({"task_id": task_id, "status": "running"})

    # GET Request: check if active task exists
    active_task_id = request.session.get('active_ai_task_id')
    if active_task_id:
        result = AsyncResult(active_task_id)
        if result.ready():
            # If it's already done (success or failed), clear session so we show fresh form
            request.session.pop('active_ai_task_id', None)
            active_task_id = None

    form = GeneratePostForm()
    return render(
        request,
        "ai_crew/generate.html",
        {
            "form": form,
            "title": "AI Post Generator",
            "recent_ai_posts": recent_ai_posts,
            "active_task_id": active_task_id,
        },
    )


@staff_member_required
@require_http_methods(["GET"])
def task_status_view(request, task_id):
    """Poll endpoint — queries Celery for status and result."""
    result = AsyncResult(task_id)
    
    # Base response for non-HTMX requests (internal API use)
    response_data = {
        "task_id": task_id,
        "status": result.status.lower(),
    }

    if result.ready():
        if "active_ai_task_id" in request.session:
            del request.session["active_ai_task_id"]

        if result.successful():
            response_data.update(result.result) # Merges the dict returned by task
        else:
            response_data.update({"status": "error", "error": str(result.result)})

    # HTMX partial rendering
    if request.headers.get("HX-Request"):
        if result.status == 'SUCCESS':
            return render(request, "ai_crew/partials/status_done.html", {"task": result.result})
        
        elif result.status == 'FAILURE' or result.status == 'REVOKED':
            error_task = {"status": "error", "error": f"Task failed: {result.result}"}
            return render(request, "ai_crew/partials/status_error.html", {"task": error_task})
        
        else:
            # Still running or pending
            progress = 5
            message = "Initializing..."
            start_time = time.time() * 1000 # Fallback
            
            logs = []
            if result.info and isinstance(result.info, dict):
                progress = result.info.get('progress', 5)
                message = result.info.get('message', 'Processing...')
                start_time = result.info.get('start_time', start_time)
                logs = result.info.get('logs', [])

            return render(request, "ai_crew/partials/status_running.html", {
                "task_id": task_id,
                "progress": progress,
                "message": message,
                "start_time": start_time,
                "logs": logs
            })

    return JsonResponse(response_data)


@staff_member_required
@require_POST
def cancel_task_view(request, task_id):
    """
    Aborts a running AI generated task via Celery revoke and clears session tracking.
    """
    if 'active_ai_task_id' in request.session:
        request.session.pop('active_ai_task_id', None)
        
    result = AsyncResult(task_id)
    result.revoke(terminate=True)  # Instantly kill the celerey worker process handling this task
    
    logger.info("Revoked celery task [id=%s]", task_id)
    
    response = HttpResponse()
    response["HX-Refresh"] = "true"
    return response
