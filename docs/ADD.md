# ADD — Architectural Design Document
## STIgma: AI-Powered Blog Platform

**Version:** 1.3.0  
**Date:** April 17, 2026  
**Status:** Active  
**Authors:** Developer Team

---

## 1. Executive Summary

STIgma is a monochrome editorial blog platform that combines a robust Django backend with a three-agent CrewAI pipeline for AI-assisted content generation. The platform features a high-end asynchronous architecture using Celery/Redis for task orchestration, HTMX/Hyperscript for a real-time "Terminal-style" editorial dashboard, and a unified monochrome design system spanning both public and admin interfaces.

---

## 2. Goals & Non-Goals

### Goals
- ✅ Provide a clean, fast, readable blog experience for public readers.
- ✅ Enable staff writers to generate AI-assisted drafts with real-time feedback.
- ✅ Maintain full editorial control: AI produces **drafts only**, humans publish.
- ✅ Use asynchronous background workers (Celery) to handle long-running LLM pipelines.
- ✅ Automatically discover and link internal content for optimized SEO.
- ✅ Generate distribution-ready content (Social Media, Newsletters) automatically.

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
                    │   Gunicorn      │  (WSGI workers)
                    └────────┬────────┘
                             │
           ┌──────────────────▼──────────────────────┐
           │              Django App                  │
           │  ┌──────────┐  ┌────────┐  ┌─────────┐  │
           │  │  blog/   │  │ai_crew/│  │ admin/  │  │
           │  └──────────┘  └───┬────┘  └─────────┘  │
           └────────────────────┼─────────────────────┘
                                │
               ┌────────────────▼───────────────┐
               │         Celery Worker          │
               │  ┌─────────────────────────┐  │
               │  │    BlogWriterCrew        │  │
               │  │  ┌────────────────────┐ │  │
               │  │  │ TopicResearcher    │ │  │
               │  │  ├────────────────────┤ │  │
               │  │  │ ContentWriter      │ │  │
               │  │  ├────────────────────┤ │  │
               │  │  │ ContentEditor      │ │  │
               │  │  │  + SearchBlogTool  │ │  │
               │  │  └────────────────────┘ │  │
               │  └─────────────────────────┘  │
               └──────────┬───────────┬────────┘
                          │           │
               ┌──────────▼──────────┐│  ┌─────────────┐
               │       Redis         │└─▶│  OpenAI API  │
               │  (Message Broker)   │   │  (LLM calls) │
               └──────────┬──────────┘   └─────────────┘
                          │
               ┌──────────▼──────────┐
               │   PostgreSQL 17     │
               │   (primary store)   │
               └─────────────────────┘
```

---

## 4. Component Design

### 4.1 Asynchronous Pipeline (`Celery + Redis`)
*   **Broker**: Redis 7.4 manages the task queue.
*   **Task**: `generate_ai_post_task` encapsulates the start-to-finish generation.
*   **State Tracking**: Celery `AsyncResult` metadata stores live progress (%), status messages, and agent "thought" logs.

### 4.2 Dynamic Frontend (HTMX & Hyperscript)
*   **Dashboard**: A "System.Exec" terminal interface built with HTMX polling.
*   **Transitions**: Hyperscript handles CSS-based transitions for form submission and status updates.
*   **Live Logs**: Multi-agent thought stream pushed via Celery metadata to the UI.
*   **Global Progress**: HTMX-driven top browser progress bar for asynchronous navigation.

### 4.3 AI Agents & Custom Tools
*   **SearchBlogTool**: A custom Django-ORM tool that allows the Editor agent to search the published post archive for internal linking opportunities.
*   **Robust JSON Extraction**: Multi-stage Markdown stripping and regex-based trailing comma correction for resilient LLM response parsing.

### 4.4 Monochrome Design System (STIgma Mono)
*   **Unified Aesthetic**: A strict black-and-white visual language using varying weights of *Playfair Display* and *IBM Plex*.
*   **Admin Bridge**: Custom CSS injection into Django Admin to remove default "Teal/Blue" styles, ensuring an editorial feel across the board.

---

## 5. Technology Stack

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| AI framework | CrewAI | ≥0.100 | Multi-agent orchestration with YAML config |
| Task Queue | Celery | 5.6.x | Distributed background task management |
| Broker / Cache | Redis | 7.4 | High-speed message passing and result storage |
| Dynamic UI | HTMX | 2.0.x | HTML-first interactivity |
| Micro-Scripting| Hyperscript | 0.9.x | High-end UI transitions and reactivity |
| Styling | TailwindCSS | 3.x | Monochrome editorial design system |

---

## 6. Performance Notes

- AI generation takes ~120s. Celery workers handle this out-of-process to keep the web server responsive.
- SQLite is NOT supported for the broker; Redis is mandatory for task metadata storage.
- The `SearchBlogTool` is read-only and restricted to `status=PUBLISHED`.

---

## 7. Future Considerations (v2)
- [ ] SEO & Distribution Automation (Phase 4).
- [ ] Image generation agent (DALL-E tool for cover images).
- [ ] TailwindCSS PostCSS build pipeline (replace CDN).
