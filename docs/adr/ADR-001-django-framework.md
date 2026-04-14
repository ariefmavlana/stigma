# ADR-001 — Use Django as the Web Framework

**Status:** Accepted  
**Date:** April 10, 2025  
**Deciders:** Engineering Team

---

## Context

We need a Python web framework to build the STIgma blog. The main candidates were:

| Option | Pros | Cons |
|--------|------|------|
| **Django** | Built-in admin, ORM, auth, migrations; massive ecosystem; LTS releases | More opinionated, heavier than micro-frameworks |
| FastAPI | Async-native, modern, fast | No built-in admin; requires more custom work |
| Flask | Lightweight, flexible | Requires assembling many parts manually |

## Decision

**Use Django 4.2 LTS.**

## Rationale

1. **Built-in admin** — The Django admin gives editors a free, powerful CMS out of the box. This is critical for a content platform where non-technical staff need to manage posts.
2. **ORM + migrations** — Django's migration system makes schema evolution safe and repeatable.
3. **django-markdownx** — Native Django package that provides a Markdown editor widget and rendering. No custom integration needed.
4. **django-taggit** — Battle-tested tag management that integrates cleanly with Django models.
5. **LTS** — Django 4.2 is an LTS release, ensuring security fixes through April 2026 at minimum.
6. **Team familiarity** — The team has existing Django expertise.

## Consequences

- **Positive:** Faster development for content management features; admin is free.
- **Positive:** Django's ORM makes complex queries (filtering by status, category, tag) simple and safe.
- **Negative:** Synchronous request handling means CrewAI (slow LLM calls) blocks the web process. Mitigated by restricting AI generation to staff only; v2 will add Celery.
- **Negative:** Slightly more boilerplate than FastAPI for pure API endpoints.
