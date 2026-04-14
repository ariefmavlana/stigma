# ADR-003 — Use PostgreSQL 17 as the Primary Database

**Status:** Accepted  
**Date:** April 10, 2025  
**Deciders:** Engineering Team

---

## Context

We need a production-grade relational database. Candidates:

| Option | Notes |
|--------|-------|
| **PostgreSQL 17** | Battle-tested, rich feature set, UUID native, full-text search |
| SQLite | Great for dev/testing; not suitable for production concurrency |
| MySQL 8 | Solid choice but weaker full-text search; less Django ecosystem love |

## Decision

**Use PostgreSQL 17 with psycopg3 (binary) as the driver.**

## Rationale

1. **UUID primary keys** — `Post` uses UUID PKs. PostgreSQL handles `uuid` natively; SQLite stores them as strings.
2. **Full-text search** — PostgreSQL's `tsvector` / `tsquery` can power a v2 search upgrade without a separate search service.
3. **Concurrency** — MVCC handles concurrent reads/writes gracefully; critical once posts scale.
4. **psycopg3** — Modern async-capable driver; aligns with the project's Python 3.12+ target. The `binary` extra uses the compiled C extension for maximum performance.
5. **Django ORM support** — First-class Django support; `django.db.backends.postgresql` is the most tested backend.
6. **Version 17** — Latest major release (2024); improved logical replication, better vacuum performance, `JSON_TABLE` support for future use.

## Consequences

- **Positive:** Reliable, scalable, rich feature set for future needs.
- **Positive:** `psycopg3` is future-proof and async-ready for Django's async views.
- **Negative:** Requires running a PostgreSQL server (not bundled). Documented in `USAGE.md`.
- **Negative:** Heavier than SQLite for pure local development — mitigated by providing `DB_*` env var defaults.
