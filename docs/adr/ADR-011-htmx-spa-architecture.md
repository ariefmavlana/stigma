# ADR-011: HTMX & Hyperscript "SPA" Architecture

## Status
Accepted

## Context
STIgma aims to provide a high-end, extremely fast editorial reading experience. Traditional Django multi-page applications suffer from full-page reloads (white flashes, lost scroll position, and slow perceived performance). Usually, solving this requires heavy JavaScript frameworks (React, Vue, Next.js), which introduces massive complexity, state management issues, and API overhead.

## Decision
We decided to transform STIgma into an SPA (Single Page Application) using **HTMX** and **Hyperscript** natively within Django templates. 

1.  **Global SPA Navigation (`hx-boost="true"`)**: By attaching `hx-boost` to the `<body>` element, all standard `<a>` links and `<form>` submissions are intercepted by HTMX, which fetches the new page via AJAX and swaps the body instantly.
2.  **Live Search Dropdown**: Implemented via `hx-get` binding to the native navigation search input, triggering on `keyup delay:300ms`, returning a specialized partial (`search_live_results.html`).
3.  **Infinite Scroll (`hx-trigger="revealed"`)**: The traditional numeric pagination in `post_list.html` has been replaced with an infinite scroll mechanism that fetches the next page partial (`post_list_items.html`) seamlessly when the user reaches the bottom.
4.  **Real-Time Commenting**: Form submissions in `post_detail.html` utilize `hx-post` to submit data and return a single `comment.html` partial, which is appended to the DOM (`hx-swap="beforeend"`) with Hyperscript animation, without a full page refresh.
5.  **Resilient Background State Tracking (`hx-trigger="load"`)**: Instead of blocking WSGI connections, long-running processes (like AI Generation via Celery) log their `task_id` into the user's local Django Session cookie. On future page reloads, HTMX intelligently restores the partials automatically (`hx-get`) using the cached Session ID, solving connection dropouts silently.

## Consequences
- **Positive**:
    - **Speed & UX**: The perceived performance is now identical to complex React/Next.js applications. 
    - **Simplicity**: No decoupled frontend, no REST/GraphQL APIs, no separate build step. We keep all the power of Django ORM and template rendering.
    - **Maintainability**: Interactivity logic is co-located with HTML elements (Locality of Behavior).
- **Neutral**:
    - Requires using Django Views to check `request.headers.get('HX-Request')` to return partials instead of full templates in some edge cases.
- **Negative**:
    - Third-party scripts (e.g., ad scripts, strict auth redirects) might need special handling since full reloads don't happen automatically.
