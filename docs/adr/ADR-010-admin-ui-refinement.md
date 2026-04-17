# ADR-010: Monochrome Editorial Design & Admin Refinement

## Status
Accepted

## Context
STIgma aims for a high-end, premium editorial aesthetic, specifically targeting the sophistication of modern NYT-style digital publications. While the public-facing site successfully uses a monochrome theme (black, white, and varying shades of grey), the default Django Admin interface (teal, blue, greens) initially created a jarring "technical" experience for Editors and Authors. This disconnect breaks the professional immersion required for an editorial-grade pipeline.

Additionally, the asynchronous nature of HTMX-driven navigation lacked a global feedback mechanism, leading to perceived latency.

## Decision
We decided to:
1.  **Unified NYT-Style CMS**: Completely rewrote the custom CSS bridge (`admin-mono.css`) into the Django Admin to override default styles with a strict monochrome language that perfectly models a traditional journalism CMS. This includes white-space heavy layouts, underline-only forms, and Playfair/Plex typography.
2.  **Editorial Layout & Save Bar**: Reorganized the `Post` model admin to prioritize editorial content. The `submit-row` was made a sticky/fixed floating bar at the bottom to ease long-form Markdown editing.
3.  **Cross-Layer Integration**: Added deep links, branding, and an expanding search bar across to unify interfaces.
4.  **Admin Live-Search via Hyperscript**: Injected HTMX & Hyperscript directly into the admin `base_site.html`. The default Django list-view search bar now triggers a `keyup delay:400ms` `hx-get` request, creating instant live-search capabilities without backend modifications.

## Consequences
- **Positive**:
    - Significantly improved Editorial experience for staff.
    - Reduced visual cognitive load by removing irrelevant technical fields.
    - Faster perceived performance due to global progress indicators.
- **Neutral**:
    - Requires maintaining a custom CSS file to ensure future Django updates don't break the layout.
- **Negative**:
    - None identified.

## Alternatives Considered
- **Third-party Admin Themes (Jazzmin/Suit)**: Rejected to maintain a lightweight, zero-dependency codebase and total control over the monochrome typography.
