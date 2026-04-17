# ✦ STIgma

> *An AI-powered editorial blog platform. Thoughts, crafted.*

STIgma is a minimal, monochrome blog built with **Django**, **CrewAI**, and **PostgreSQL 17**. It ships a complete editorial experience — clean reading UI, rich admin, and a three-agent AI pipeline that researches, writes, and edits draft posts at the press of a button.

---

## What It Does

**For readers:** A beautiful, typography-forward blog with fast page loads, post search, category and tag browsing, and a comment system.

**For editors:** A powerful Django admin with Markdown editing, rich post metadata, and comment moderation.

**For content teams:** An AI generation workflow powered by three specialist CrewAI agents — every AI-assisted draft is clearly labelled and requires human review before publishing.

---

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12 (uv) |
| Web Framework | Django 4.2 LTS |
| Dynamic UI | HTMX + Hyperscript |
| AI Pipeline | CrewAI + SerperDev |
| Styling | TailwindCSS |
| Documentation | ADD + ADR (Standards) |

---

## CrewAI Agents

```
┌──────────────────────────────────────────────────┐
│              BlogWriterCrew                       │
│                                                  │
│  1. TopicResearcher                              │
│     Goal: Deep, multi-angle research             │
│     Tools: SerperDevTool, WebsiteSearchTool      │
│                    ↓                             │
│  2. ContentWriter                                │
│     Goal: Compelling 800–1200 word Markdown post │
│     Input: Research brief                        │
│                    ↓                             │
│  3. ContentEditor                                │
│     Goal: Polish, SEO, output structured JSON    │
│     Output: {title, excerpt, tags, body, ...}    │
└──────────────────────────────────────────────────┘
```

All agents are defined in `ai_crew/config/agents.yaml` with specialist roles, goals, and detailed backstories. Tasks are in `ai_crew/config/tasks.yaml`. The crew uses the official CrewAI `@CrewBase` pattern.

---

## Quick Start

```bash
# 1. Install dependencies
uv sync

# 2. Configure environment
cp .env.example .env
# Edit .env with your DB credentials, OPENAI_API_KEY, SERPER_API_KEY

# 3. Run migrations
uv run python manage.py migrate

# 4. Create admin user
uv run python manage.py createsuperuser

# 5. Start server
uv run python manage.py runserver
```

Full setup guide: **[docs/USAGE.md](docs/USAGE.md)**

---

## Documentation

| Document | Description |
|----------|-------------|
| [docs/ADD.md](docs/ADD.md) | **Architectural Design Document** — full system design |
| [docs/USAGE.md](docs/USAGE.md) | **Usage Guide** — setup, generation, and deployment |
| [docs/CHANGELOG.md](docs/CHANGELOG.md) | **Changelog** — history of advanced features |
| [docs/adr/](docs/adr/) | **Architecture Decision Records** — why we built it this way |

---

## Project Structure

```
stigma/
├── pyproject.toml              # uv project config + dependencies
├── .env.example                # environment variable template
├── manage.py
│
├── stigma/                    # Django project
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── blog/                       # Blog application
│   ├── models.py               # Post, Category, Comment
│   ├── views.py                # All public views
│   ├── admin.py                # Rich editor admin
│   ├── forms.py                # CommentForm
│   ├── urls.py
│   └── context_processors.py
│
├── ai_crew/                    # CrewAI integration
│   ├── crew.py                 # BlogWriterCrew (@CrewBase)
│   ├── config/
│   │   ├── agents.yaml         # 3 specialist agent definitions
│   │   └── tasks.yaml          # 3 sequential task definitions
│   ├── views.py                # Generate + API endpoints
│   ├── forms.py                # GeneratePostForm
│   └── urls.py
│
├── templates/                  # Django HTML templates
│   ├── base.html               # Monochrome editorial layout
│   ├── blog/
│   │   ├── home.html
│   │   ├── post_detail.html
│   │   ├── post_list.html
│   │   ├── category_detail.html
│   │   ├── tag_detail.html
│   │   ├── search.html
│   │   └── about.html
│   └── ai_crew/
│       └── generate.html
│
├── static/                     # Static assets
└── docs/                       # Documentation
    ├── ADD.md
    ├── CHANGELOG.md             # Advanced phase history
    ├── USAGE.md
    └── adr/
        ├── ADR-001-django-framework.md
        ├── ADR-002-crewai-integration.md
        ├── ADR-003-postgresql.md
        ├── ADR-004-tailwindcss.md
        ├── ADR-005-htmx-hyperscript.md        # New
        └── ADR-006-threading-task-management.md # New
```

---

## License

MIT — see `LICENSE` for details.

---

*Built with Django & CrewAI. Every AI-assisted post is clearly marked and human-reviewed before publication.*
