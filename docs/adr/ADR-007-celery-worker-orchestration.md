# ADR-007: Celery Worker Orchestration for AI Workflows

## Context
Generation of AI content via CrewAI can take 2–10 minutes depending on the complexity and LLM response times.
Previously, we used a custom `threading.Thread` implementation with an in-memory dictionary to track tasks.

### Problems with Threading:
1. **Volatility**: If the Django process restarts, all in-memory task states are lost.
2. **Resource Management**: Threads compete with the web process for CPU and memory.
3. **Lack of Control**: No easy way to retry, schedule, or prioritize tasks.
4. **Visibility**: Monitoring active threads is difficult.

## Decision
We will migrate to **Celery** with **Redis** as the message broker.

1. **Celery** handles the distributed task queue.
2. **Redis** stores the queue and the result backend.
3. **AsyncResult** is used in Django views to track progress across page refreshes.

## Architecture
- **Broker**: Redis (running via Docker).
- **Backend**: Redis (stores JSON results of finished tasks).
- **Workers**: A separate process (`celery -A stigma worker`) runs the actual CrewAI logic.

## Consequences

### Positive
- **Stability**: Tasks persist even if the web server restarts.
- **Separation of Concerns**: The web process only handles HTTP requests; workers handle heavy compute.
- **Scalability**: We can spin up multiple workers across different machines if needed.
- **Rich Monitoring**: Tools like Flower can be added later for visual queue management.

### Negative
- **Dev Complexity**: Requires running Redis and a separate Worker process during development.
- **Infrastructure Cost**: Redis requires RAM and storage.

## Alternatives Considered
- **Subprocess**: Still runs on the same machine and harder to track.
- **Django Q**: Good alternative, but Celery is more industry-standard for complex AI pipelines.
- **Redis Queue (RQ)**: Simpler than Celery, but lacks some of the state-tracking features we need for real-time progress.
