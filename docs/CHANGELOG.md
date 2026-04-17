# Changelog — STIgma

All notable changes to the STIgma project will be documented in this file.

## [Advanced Phase] — 2026-04-17

### Added
- **HTMX 2.0.8 & Hyperscript 0.9.91 Updates**: Ensured latest stable versions.
- **Phase 1: Celery & Redis Orchestration**:
  - Replaced manual threading with a production-grade worker system.
  - Redis broker running via Docker Compose.
  - Background task state tracking with `AsyncResult`.
  - Added [ADR-007](docs/adr/ADR-007-celery-worker-orchestration.md).
- **Phase 2: Premium UI/UX (HTMX & Hyperscript)**:
  - Implemented real-time **Agent Thought Stream** via CrewAI step callbacks.
  - Redesigned the generator dashboard with high-end monochrome aesthetics.
  - Added smooth state transitions and terminal-style progress logs.
  - Interactive history table for recent AI activity.
- **Dynamic AI Generator Flow**:
  - Live progress tracking using HTMX polling (`hx-trigger="every 3s"`).
  - Real-time elapsed timer and animated progress bar using Hyperscript.
  - New modular partials for UI states: `status_running.html`, `status_done.html`, `status_error.html`.
- **Architectural Documentation**:
  - **[ADR-005](file:///home/ariefmavl/learning/cerdascrew/stigma/docs/adr/ADR-005-htmx-hyperscript.md)**: Adopting a declarative frontend approach.
  - **[ADR-006](file:///home/ariefmavl/learning/cerdascrew/stigma/docs/adr/ADR-006-threading-task-management.md)**: Implementing lightweight async task management via threading.

### Changed
- **Frontend Refactoring**: Removed ~200 lines of custom vanilla JavaScript in `generate.html`.
- **Post Preview**: Updated `blog.views.post_detail` to allow staff members to preview `DRAFT` posts.
- **UI/UX Polish**: Improved the "Staff Only" badges and refined the AI Badge aesthetics.

### Fixed
- Fixed `NameError` in `task_status_view` regarding task dictionary access.
- Corrected Django template syntax in Hyperscript attributes in `status_running.html`.
- Resolved 404 errors when previewing newly generated AI drafts.

---

## [v1.0.0] — 2026-04-10
### Added
- Initial release of STIgma blog engine.
- Three-agent CrewAI pipeline (Researcher, Writer, Editor).
- Monochrome editorial UI based on Tailwind CSS.
- PostgreSQL 17 integration.
- MarkdownX support for admin editing.
