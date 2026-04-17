# ADD — Architectural Design Document
## STIgma: AI-Powered Blog Platform

**Version:** 1.0.0  
**Date:** April 10, 2025  
**Status:** Active  
**Authors:** Engineering Team

---

## 1. Executive Summary

STIgma is a monochrome editorial blog platform that combines a robust Django backend with a three-agent CrewAI pipeline for AI-assisted content generation. The platform targets content teams who want to ship high-quality, research-backed posts faster without sacrificing editorial control.

---

## 2. Goals & Non-Goals

### Goals
- ✅ Provide a clean, fast, readable blog experience for public readers
- ✅ Enable staff writers to generate AI-assisted drafts in one click
- ✅ Maintain full editorial control: AI produces **drafts only**, humans publish
- ✅ Use only well-maintained, documented open-source tools
- ✅ Be deployable on a single server with minimal ops overhead

### Non-Goals
- ❌ Real-time collaboration (out of scope for v1)
- ❌ Newsletter / email delivery (v2 consideration)
- ❌ Multi-tenant / SaaS mode
- ❌ Comment spam filtering (manual moderation only in v1)

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Public Internet                          │
└────────────────────────────┬────────────────────────────────────┘
                             │  HTTPS
                    ┌────────▼────────┐
                    │   Nginx / CDN   │  (static files, SSL termination)
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Gunicorn      │  (WSGI, 4 workers)
                    └────────┬────────┘
                             │
          ┌──────────────────▼──────────────────────┐
          │              Django App                  │
          │  ┌──────────┐  ┌────────┐  ┌─────────┐  │
          │  │  blog/   │  │ai_crew/│  │ admin/  │  │
          │  └──────────┘  └───┬────┘  └─────────┘  │
          └───────────────────┬┘────────────────────┘
                              │
              ┌───────────────▼───────────────┐
              │         CrewAI Layer           │
              │  ┌─────────────────────────┐  │
              │  │    BlogWriterCrew        │  │
              │  │  ┌────────────────────┐ │  │
              │  │  │ TopicResearcher    │ │  │
              │  │  │  + SerperDevTool   │ │  │
              │  │  │  + WebsiteSearch   │ │  │
              │  │  ├────────────────────┤ │  │
              │  │  │ ContentWriter      │ │  │
              │  │  ├────────────────────┤ │  │
              │  │  │ ContentEditor      │ │  │
              │  │  └────────────────────┘ │  │
              │  └─────────────────────────┘  │
              └──────────┬────────────────────┘
                         │
              ┌──────────▼──────────┐    ┌─────────────┐
              │   PostgreSQL 17     │    │  OpenAI API  │
              │   (primary store)   │    │  (LLM calls) │
              └─────────────────────┘    └─────────────┘
```

---

## 4. Component Design

### 4.1 Django Blog App (`blog/`)

| Component | Responsibility |
|-----------|---------------|
| `models.py` | `Post`, `Category`, `Comment` — core data models |
| `views.py` | All public views: home, post detail, listing, search |
| `admin.py` | Rich admin for editors (MarkdownX integration) |
| `forms.py` | `CommentForm` for reader comments |
| `context_processors.py` | Global template context (blog name, categories) |

**Post lifecycle:**
```
DRAFT → PUBLISHED → (optional) ARCHIVED
```
AI-generated posts always start as `DRAFT`. Only staff can set `PUBLISHED`.

### 4.2 CrewAI App (`ai_crew/`)

| Component | Responsibility |
|-----------|---------------|
| `crew.py` | `BlogWriterCrew` — `@CrewBase` class with 3 agents + 3 tasks |
| `config/agents.yaml` | Agent roles, goals, backstories |
| `config/tasks.yaml` | Task descriptions, expected outputs, context dependencies |
| `views.py` | Django views to trigger crew, parse JSON, save draft |
| `forms.py` | `GeneratePostForm` — topic, audience, tone, category |

**CrewAI sequential flow:**
```
inputs: {topic, target_audience, tone}
    │
    ▼
[research_task] → TopicResearcher
    Uses: SerperDevTool, WebsiteSearchTool
    Output: structured research brief (Markdown)
    │
    ▼
[write_task] → ContentWriter
    Receives: research_task context
    Output: full 800–1200 word Markdown draft
    │
    ▼
[edit_task] → ContentEditor
    Receives: research_task + write_task context
    Output: JSON { title, meta_description, excerpt, tags, body }
    │
    ▼
Django view: parse JSON → save Post(status=DRAFT, is_ai_generated=True)
```

### 4.3 Data Models

```python
Category:  id, name, slug, description
Post:      id (UUID), title, slug, body (Markdown), excerpt,
           category (FK), tags (M2M via django-taggit),
           author (FK User), status, is_ai_generated,
           reading_time, views, published_at
Comment:   id, post (FK), author_name, author_email,
           body, is_approved
```

---

## 5. Technology Stack

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| Language | Python | 3.12 | LTS, performance improvements, type hints |
| Package manager | uv | latest | Fast, deterministic, Rust-based |
| Web framework | Django | 4.2 LTS | Battle-tested, excellent ORM, admin |
| Database | PostgreSQL | 17 | Reliability, full-text search, UUID support |
| DB driver | psycopg3 (binary) | ≥3.1 | Async-ready, PostgreSQL 17 native |
| AI framework | CrewAI | ≥0.100 | Role-based multi-agent, YAML config, active dev |
| AI tools | crewai-tools | ≥0.33 | SerperDevTool, WebsiteSearchTool built-in |
| Markdown | django-markdownx | 4.x | Editor widget + rendering |
| Tagging | django-taggit | 5.x | Industry standard Django tagging |
| Static files | WhiteNoise | 6.x | Zero-config static serving |
| Frontend | TailwindCSS (CDN) | 3.x | Utility-first, no build step for v1 |
| Dynamic UI | HTMX | 2.0.8 | Declarative AJAX, polling, and partial updates |
| Micro-Interactions| Hyperscript | 0.9.91 | Hyper-declarative UI micro-scripting |
| Fonts | Playfair Display + IBM Plex Serif | — | Editorial, distinctive, monochrome-fit |

---

## 6. Security Considerations

- All AI generation endpoints are `@staff_member_required` — public users cannot trigger LLM calls
- CSRF protection on all POST forms
- Comment moderation: comments are `is_approved=False` by default
- API keys stored in `.env`, never committed to VCS
- `bleach` available for sanitising any user-generated HTML
- `SECRET_KEY` must be rotated in production

---

## 7. Performance Notes

- Post view counts use `F()` expressions (atomic increment, no race condition)
- Database indexes on `(status, published_at)` and `slug` for fast listing queries
- WhiteNoise + `CompressedManifestStaticFilesStorage` for production static files
- CrewAI runs in **daemon background threads** (`threading.Thread`) controlled by a `lock` for thread safety. This prevents HTTP timeouts during long LLM runs without requiring a full Celery/Redis infrastructure.

---

## 8. Future Considerations (v2)

- [x] HTMX + Hyperscript integration for dynamic UI
- [x] Background generation using threading (ADR-006)
- [ ] Celery + Redis for deep scalability (production grade)
- [ ] Image generation agent (DALL-E tool for cover images)
- [ ] TailwindCSS PostCSS build pipeline (replace CDN)
- [ ] Full-text search via PostgreSQL `tsvector` or Meilisearch
- [ ] RSS feed endpoint
