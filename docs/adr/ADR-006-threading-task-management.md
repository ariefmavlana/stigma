# ADR-006: Lightweight Asynchronous Task Management via Threading

## Status
Active

## Context
CrewAI generation tasks typically take 2–5 minutes due to multiple LLM calls and web searching. Running these synchronously within a Django request would cause HTTP timeouts (Gunicorn/Nginx) and a poor user experience. While Celery/Redis is the industry standard for background tasks, it introduces significant operational complexity (extra containers, message brokers) for a single-server deployment.

## Decision
For the initial "Advanced" phase, we have implemented an **asynchronous threading strategy** using Python's `threading.Thread`:

1.  Tasks are initialized in a global, thread-safe dictionary (`_tasks`) protected by a `threading.Lock`.
2.  The `kickoff()` method runs in a daemon thread.
3.  The frontend polls a status endpoint using **HTMX**, which returns HTML fragments based on the current state in the in-memory store.

## Consequences
*   **Positives**:
    *   **Zero Infrastructure Overhead**: No need for Redis or Celery workers.
    *   **Immediate Feedback**: Users get a `task_id` and "Running" state instantly.
    *   **Simplicity**: The entire logic remains within the Django application.
*   **Negatives**:
    *   **Volatile State**: If the server restarts, all in-progress or completed task records in memory are lost (mitigated by the fact that successful posts are saved to the database).
    *   **Scalability**: This approach is not suitable for high-concurrency environments or multi-node deployments (where an in-memory dict isn't shared).

## Future Evolution
Should the platform scale to multiple staff members or high traffic, this strategy will be migrated to **Celery + Redis**, as noted in the ADD's future considerations.
