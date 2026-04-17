import json
import logging
from celery import shared_task
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from django.db import close_old_connections

from blog.models import Post, Category
from .crew import BlogWriterCrew, BlogWriterCrewID

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
    raw = re.sub(r",\s*(\}|\])", r"\1", raw)
    
    return raw.strip()


def _make_step_callback(celery_task, start_time: float, logs: list, language: str):
    """
    Factory for a CrewAI step_callback compatible with CrewAI >= 0.80.
    The callback receives a single argument (the step output object).
    """
    is_id = language.lower() in {"id", "id-id", "indonesia", "indonesian", "bahasa indonesia", "bahasa"}

    def step_callback(step_output) -> None:
        message = ""

        if hasattr(step_output, 'thought') and step_output.thought:
            message = step_output.thought
        elif hasattr(step_output, 'tool') and step_output.tool:
            tool_input = getattr(step_output, 'tool_input', '')
            if isinstance(tool_input, str):
                tool_input = tool_input[:60]
            prefix = "Menggunakan tool" if is_id else "Using tool"
            message = f"{prefix}: {step_output.tool}"
            if tool_input:
                message += f" → {tool_input}..."
        elif hasattr(step_output, 'output') and step_output.output:
            message = "Agen menyelesaikan satu bagian tugas." if is_id else "Agent completed a task section."
        elif hasattr(step_output, 'text') and step_output.text:
            message = step_output.text[:120]
        else:
            message = "Agen sedang memproses..." if is_id else "Agent is processing..."

        # Limit message length for the UI terminal
        message = (message[:150] + '...') if len(message) > 150 else message

        # Avoid duplicate consecutive logs
        if not logs or logs[-1] != message:
            logs.append(message)
            if len(logs) > 15:
                logs.pop(0)

        celery_task.update_state(
            state='PROGRESS',
            meta={
                'progress': 50,
                'message': message,
                'start_time': start_time,
                'logs': list(logs),
                'language': language,
            }
        )

    return step_callback


@shared_task(bind=True)
def generate_ai_post_task(self, topic, target_audience, tone, language, category_id, user_id, start_time):
    """
    Celery task to run the BlogWriterCrew pipeline.
    Polls CrewAI step_callback to update live logs via Celery state.
    """
    close_old_connections()
    
    is_id = language.lower() in {"id", "id-id", "indonesia", "indonesian", "bahasa indonesia", "bahasa"}
    
    logs = [
        "Menginisialisasi pekerja..." if is_id else "Initializing workers...",
        "Membangun jembatan LLM..." if is_id else "Building LLM bridge...",
    ]

    try:
        self.update_state(state='PROGRESS', meta={
            'progress': 5,
            'message': 'Menginisialisasi Kru...' if is_id else 'Initializing Crew...',
            'start_time': start_time,
            'logs': logs,
            'language': language,
            'stage': 'init',
        })

        user = User.objects.get(pk=user_id)

        # Build the live callback
        callback = _make_step_callback(self, start_time, logs, language)

        self.update_state(state='PROGRESS', meta={
            'progress': 15,
            'message': 'Agen sedang menginisialisasi...' if is_id else 'Agents are initializing...',
            'start_time': start_time,
            'logs': logs,
            'language': language,
            'stage': 'init',
        })

        # Select crew based on language
        id_aliases = {"id", "id-id", "indonesia", "indonesian", "bahasa indonesia", "bahasa"}
        active_crew_cls = BlogWriterCrewID if language.lower() in id_aliases else BlogWriterCrew

        # Instantiate crew and inject the step_callback into the Crew object
        crew_instance = active_crew_cls()
        crewai_crew = crew_instance.crew()
        crewai_crew.step_callback = callback

        self.update_state(state='PROGRESS', meta={
            'progress': 20,
            'message': '🔍 Agen sedang meneliti topik...' if is_id else '🔍 Agents are researching...',
            'start_time': start_time,
            'logs': logs,
            'language': language,
            'stage': 'research',
        })

        result = crewai_crew.kickoff(
            inputs={
                "topic": topic,
                "target_audience": target_audience,
                "tone": tone,
                "language": language,
            }
        )

        raw = _clean_json(result.raw)

        # Log internal link discovery
        if "/posts/" in raw:
            logs.append("Tautan internal ditemukan dan diintegrasikan." if is_id else "Internal links discovered and integrated.")
        else:
            logs.append("Tidak ditemukan tautan internal yang sesuai." if is_id else "No suitable internal links found by agent.")

        self.update_state(state='PROGRESS', meta={
            'progress': 90,
            'message': '✅ Menyelesaikan draf...' if is_id else '✅ Finalizing draft...',
            'start_time': start_time,
            'logs': logs + [
                "Tugas selesai. Mengurai data struktural..." if is_id else "Task complete. Parsing structural data..."
            ],
            'language': language,
            'stage': 'finalizing',
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

        # Honour AI-provided reading time if valid
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
            "language": language,
            "logs": logs + [
                "✓ Sukses! Post tersimpan sebagai draf." if is_id else "✓ Success! Post saved as draft."
            ]
        }

    except json.JSONDecodeError as exc:
        logger.error("JSON parse error after generation [task=%s]: %s", self.request.id, exc)
        logger.debug("Raw output that failed to parse: %s", result.raw[:500] if 'result' in dir() else "N/A")
        raise exc

    except Exception as exc:
        logger.exception("Celery task error [task=%s]", self.request.id)
        raise exc

    finally:
        close_old_connections()
