# ADR-004 — Use TailwindCSS for Frontend Styling

**Status:** Accepted  
**Date:** April 10, 2025  
**Deciders:** Engineering Team

---

## Context

We need a CSS approach for the blog frontend. Options considered:

| Option | Notes |
|--------|-------|
| **TailwindCSS** | Utility-first; consistent design system; great for component-like templates |
| Bootstrap 5 | Pre-built components; opinionated aesthetic; harder to customise |
| Vanilla CSS | Full control; no toolchain; verbose for complex designs |
| Bulma | Clean defaults; less customisable than Tailwind |

## Decision

**Use TailwindCSS via CDN for v1, with a note to migrate to PostCSS build pipeline in v2.**

## Rationale

1. **Design consistency** — Tailwind's design tokens (spacing, colors, typography) ensure the monochrome aesthetic stays coherent across all templates.
2. **Customisable** — The `tailwind.config` block in `base.html` extends the default palette with `ink-*` colours and custom font families (`display`, `body`, `mono`) perfectly suited to our editorial design.
3. **CDN for v1** — Avoids Node.js / npm as a build dependency. For a team focused on Python/Django, this reduces onboarding friction significantly.
4. **Utility classes over components** — Django templates with utility classes are readable and require no JS framework or component abstraction layer.
5. **No unused CSS in CDN** — TailwindCSS CDN v3 uses the JIT engine which generates only the classes used in the page at runtime (browser-side in CDN mode).

## Consequences

- **Positive:** Fast to build, easy to customise, no frontend build step in v1.
- **Positive:** Custom `ink-*` palette integrates seamlessly with Tailwind's system.
- **Negative:** CDN mode loads the full Tailwind runtime (~90KB gzipped) in the browser. For v2, replace with a PostCSS build step to ship only used utilities (~5–15KB).
- **Negative:** `line-clamp-*` utilities require the `@tailwindcss/line-clamp` plugin in PostCSS mode (not an issue with CDN).

## Migration Path (v2)

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init
# Move <script>tailwind.config</script> to tailwind.config.js
# Add build step to pyproject.toml scripts
```
