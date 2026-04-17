import json
import logging
from celery import shared_task
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from django.db import close_old_connections

from blog.models import Post, Category
from .crew import BlogWriterCrew

logger = logging.getLogger(__name__)

def _clean_json(raw: str) -> str:
    """Strip markdown fences and leading prose — return only the JSON object."""
    import re
    raw = raw.strip()
    raw = re.sub(r"^```[a-zA-Z]*\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()
    
    # Extract the first { to the last }
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        raw = raw[start : end + 1]
    
    # Handle trailing commas (common LLM error)
    # This removes a comma if it's followed by a closing brace or bracket
    raw = re.sub(r",\s*(\}|\])", r"\1", raw)
    
    return raw.strip()


def create_crew_callback(celery_task, start_time, current_logs):
    """
    Creates a callback for CrewAI to update Celery state after every step.
    """
    def step_callback(step_output):
        # type(step_output) can be AgentAction, ToolResult, or AgentFinish
        message = ""
        
        if hasattr(step_output, 'thought') and step_output.thought:
            message = step_output.thought
        elif hasattr(step_output, 'tool') and step_output.tool:
            message = f"Agent using {step_output.tool}..."
        elif hasattr(step_output, 'output') and step_output.output:
            # Likely an AgentFinish
            message = "Agent finalized a task section."
        else:
            message = "Agent is processing complex logic..."
            
        # Limit message length for the UI terminal
        message = (message[:100] + '...') if len(message) > 100 else message
        
        # Avoid duplicate consecutive logs
        if not current_logs or current_logs[-1] != message:
            current_logs.append(message)
            if len(current_logs) > 12:
                current_logs.pop(0)
            
        celery_task.update_state(
            state='PROGRESS',
            meta={
                'progress': 50, # Intermediate progress
                'message': message,
                'start_time': start_time,
                'logs': list(current_logs)
            }
        )
    return step_callback

@shared_task(bind=True)
def generate_ai_post_task(self, topic, target_audience, tone, language, category_id, user_id, start_time):
    """
    Celery task to run the BlogWriterCrew.
    Updates task state with live logs via step_callback.
    """
    close_old_connections()
    logs = ["Initializing workers...", "Building LLM bridge..."]
    
    try:
        self.update_state(state='PROGRESS', meta={
            'progress': 10, 
            'message': 'Initializing Crew...',
            'start_time': start_time,
            'logs': logs
        })
        
        user = User.objects.get(pk=user_id)
        
        # Define the callback
        callback = create_crew_callback(self, start_time, logs)
        
        self.update_state(state='PROGRESS', meta={
            'progress': 20, 
            'message': 'Agents are researching...',
            'start_time': start_time,
            'logs': logs
        })
        
        # Pass the callback to the crew
        result = BlogWriterCrew().crew(step_callback=callback).kickoff(
            inputs={
                "topic": topic,
                "target_audience": target_audience,
                "tone": tone,
                "language": language,
            }
        )
        
        raw = _clean_json(result.raw)
        
        # Phase 3 Verification Log
        if "[/posts/" in raw:
            logs.append("Internal links discovered and integrated.")
        else:
            logs.append("No suitable internal links found by agent.")

        self.update_state(state='PROGRESS', meta={
            'progress': 90, 
            'message': 'Finalizing draft...',
            'start_time': start_time,
            'logs': logs + ["Task complete. Parsing structural data..."]
        })
        
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

        post_url = post.get_absolute_url()
        # Fallback to a default domain if SITE_URL is not set (e.g. for development)
        site_url = getattr(settings, "SITE_URL", "http://localhost:8000").rstrip("/")
        absolute_url = f"{site_url}{post_url}"

        return {
            "status": "done",
            "post_id": str(post.pk),
            "post_title": post.title,
            "post_admin_url": f"/admin/blog/post/{post.pk}/change/",
            "post_public_url": post_url,
            "post_absolute_url": absolute_url,
            "excerpt": (post.excerpt or "")[:280],
            "tags": list(post.tags.names()),
            "reading_time": post.reading_time,
            "social_twitter": post_data.get("social_twitter", []),
            "social_linkedin": post_data.get("social_linkedin", ""),
            "newsletter_copy": post_data.get("newsletter_copy", ""),
            "logs": logs + ["Success! Post and distribution drafts saved."]
        }


    except Exception as exc:
        logger.exception("Celery task error [task=%s]", self.request.id)
        raise exc
    finally:
        close_old_connections()
