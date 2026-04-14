# ADR-002 — Use CrewAI for Multi-Agent Content Generation

**Status:** Accepted  
**Date:** April 10, 2025  
**Deciders:** Engineering Team

---

## Context

We want AI-assisted blog post generation. Options considered:

| Option | Description |
|--------|-------------|
| **CrewAI** | Role-based multi-agent framework; YAML config; specialist agents |
| Single LLM call | One prompt, one response — simple but shallow |
| LangChain | Flexible but complex; heavy dependency graph |
| AutoGen | Microsoft's framework; less mature YAML tooling |

## Decision

**Use CrewAI ≥0.100 with the `@CrewBase` pattern and YAML configuration.**

## Rationale

### Why multi-agent over a single prompt?
A single "write me a blog post about X" prompt produces generic output. A pipeline of specialists produces dramatically better results:

1. **Researcher** — Finds actual current data, quotes, trends. Uses `SerperDevTool` to search the real web.
2. **Writer** — Focuses purely on narrative architecture and prose, fed rich research context.
3. **Editor** — Reviews the draft with fresh eyes, enforces SEO, outputs structured JSON.

Each agent can be individually optimised and has a focused `goal` and `backstory` that shapes LLM behaviour.

### Why CrewAI over LangChain?
- CrewAI is standalone (no LangChain dependency) → faster, lighter
- The `@CrewBase` + YAML pattern is clean and easy to modify without touching Python
- Built-in `SerperDevTool` and `WebsiteSearchTool` in `crewai-tools`
- Active development; `crewai_tools` has PostgreSQL, file, web tools out of the box
- 100k+ certified developers — strong community support

### Why YAML config for agents/tasks?
- Separates configuration from code (12-factor app principle)
- Non-engineers can adjust agent goals/backstories without touching `crew.py`
- Matches the official CrewAI documentation pattern exactly

## Consequences

- **Positive:** Significantly higher quality output than single-prompt approaches.
- **Positive:** Modular — agents can be swapped, added, or removed independently.
- **Positive:** YAML config is readable, versionable, and auditable.
- **Negative:** Requires `OPENAI_API_KEY` (or another LLM provider) and `SERPER_API_KEY`.
- **Negative:** Synchronous execution (2–5 min) blocks the request thread. Staff-only endpoint mitigates impact; Celery is the v2 solution.
- **Negative:** LLM API costs apply per generation. Monitor with OpenAI usage dashboard.
