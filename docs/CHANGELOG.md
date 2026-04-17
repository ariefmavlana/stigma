# Changelog — STIgma

All notable changes to the STIgma project will be documented in this file.

## [v1.4.0] — 2026-04-17
### Added
- **Global SPA Architecture**: Implemented `hx-boost` in the master template to transform the traditional multi-page Django webapp into a high-speed Single Page Application without any JavaScript framework overhead.
- **Resilient AI Generation**: Engineered session-based HTMX polling (`active_ai_task_id`); AI generation processes survive page reloads and instantly restore the active progress terminal state utilizing the `hx-trigger="load"` capability.
- **Bilingual AI Pipelines**: Native prompt integration allowing AI models to research, rewrite, and finalize articles seamlessly in English or Bahasa Indonesia.
- **Hyperscript Transitions**: Integrated `htmx:beforeRequest` and `htmx:afterSettle` to provide butter-smooth fade transitions during global `.htmx-swapping`.
- **Infinite Scroll**: Modernized `post_list.html` to automatically load older posts on scroll (`hx-trigger="revealed"`) via DOM appending.
- **Real-Time Commenting**: Re-engineered the discussion section (`post_detail.html`) to submit and append comments asynchronously via `hx-post` and dynamic HTML partials.
- **Live Search Overlay**: Refactored the Hyperscript search bar to immediately stream search results via `hx-get` into a floating dropdown on `keyup`.
- **Cross-Lingual Guardrails [ADR-012]**: Injected explicit translation boundaries to AI tasks, resolving `504 Gateway Timeouts` masking as JSON syntax failures when generating non-English content.
- **Dual-Configuration CrewAI System**: Re-engineered `agents.yaml` and `tasks.yaml` into separated `_en` and `_id` localization files, enabling 100% native Indonesian language AI reasoning and logic tracking without sacrificing multi-lingual dynamic generation.
- **NYT-Style Editorial Frontend**: Completely redesigned the `home.html` to mirror a 3-column newspaper grid layout with clear dividing rules and removed modern card aesthetics.
- **Refined Reading Experience**: Narrowed the `post_list.html` width constraint down to `max-w-4xl` for an enhanced, focused reading journey.
- **Target Audience Dynamic Select**: Shifted the generic audience text input to a powerful HTML5 `<datalist>` supporting custom typings alongside curated demographics.
- **Dynamic Drop Caps & Read Progress**: Added CSS logic for automatic article drop caps and an interactive scrolling progress bar via Hyperscript.
- **NYT-CMS Admin Overhaul**: Replaced the default Django admin styling with a sophisticated, professional white-space heavy CMS design (`admin-mono.css`), featuring sticky save bars and underline-only form inputs.
- **Hyperscript Search Toggle**: Added an inline, expanding search toggle in the public navigation bar.

## [v1.3.0] — 2026-04-17

### Added
- **Admin Monochrome Bridge**: Custom CSS injection to unify the admin panel with the frontend aesthetic.
- **HTMX Global Progress System**: Added a top-bar progress indicator for all asynchronous navigation and requests.
- **Enhanced UI Interactivity**: Implemented subtle "hover-lift" on blog cards and dynamic terminal log animations.
- **Integrated Admin Shortcuts**: Unified titles and added deep links for faster editorial navigation.
- **[ADR-010](docs/adr/ADR-010-admin-ui-refinement.md)**: Formalized the monochrome editorial design system.

### Fixed
- **JSON Parsing Robustness**: Enhanced `_clean_json` with automated trailing comma removal to prevent pipeline crashes from non-standard LLM output.
- **Feedback Loops**: Fixed missing visual confirmation when copying drafs from the Distribution Dashboard.

---

## [Phase 4: Advanced] — 2026-04-17


## [v1.0.0] — 2026-04-10
### Added
- Initial release of STIgma blog engine.
- Three-agent CrewAI pipeline (Researcher, Writer, Editor).
- Monochrome editorial UI based on Tailwind CSS.
- PostgreSQL 17 integration.
- MarkdownX support for admin editing.
