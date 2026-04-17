# ADR-005: Integration of HTMX and Hyperscript

## Status
Proposed

## Context
The current implementation of the "AI Post Generator" relies on vanilla JavaScript for handling asynchronous form submissions, polling task status, and updating the UI. While functional, this approach leads to verbose JavaScript.

| Frontend | TailwindCSS (CDN) | 3.x | Utility-first, no build step for v1 |
| Dynamic UI | HTMX | 2.0.0 | Declarative AJAX, polling, and partial updates |
| Micro-Interactions| Hyperscript | 0.9.12 | Hyper-declarative UI micro-scripting |

## Decision
We will integrate **HTMX 2.0.8** and **Hyperscript 0.9.91** into the frontend stack.

1.  **HTMX** will be used for:
    *   Asynchronous form submissions (AJAX).
    *   Polling server status without manual `fetch` loops (using `hx-trigger="every 3s"`).
    *   Partial HTML fragment updates from the server, improving perceived performance.
2.  **Hyperscript** will be used for:
    *   Client-side micro-interactions (toggling classes, visibility, disabling buttons).
    *   Calculating and displaying live timers (`Date.now()`) without vanilla boilerplate.
    *   Replacing repetitive DOM manipulation code within templates.

## Consequences
*   **Positives**:
    *   **Zero JS Overload**: Removed ~200 lines of custom vanilla JS in the `generate` view.
    *   **Declarative UI**: UI states (Running, Done, Error) are now managed by pure HTML fragments.
    *   **Improved maintainability**: Templates are self-describing.
*   **Negatives**:
    *   Requires HTMX/Hyperscript CDNs (mitigated by small footprint).
