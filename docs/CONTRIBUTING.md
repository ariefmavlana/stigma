# Contributing to STIgma

## Development Setup

```bash
# Clone and enter
cd ~/learning/stigma

# Install all deps including dev tools
uv sync

# Set up pre-commit (optional but recommended)
uv run pre-commit install
```

## Code Style

- **Python:** Black formatting, Ruff for linting
  ```bash
  uv run black .
  uv run ruff check . --fix
  ```
- **Templates:** 2-space indent, Tailwind classes alphabetically grouped by concern
- **YAML (CrewAI):** Keep agent goals/backstories rich — they directly affect output quality

## Making Changes to Agents

Agent definitions live in `ai_crew/config/agents.yaml`. Before changing:

1. Understand what the agent is optimised for (read its current `backstory` carefully)
2. Test with a low-cost model first (`gpt-4o-mini`)
3. Document the change and why in the PR description

## Adding a New View

1. Add the view function to `blog/views.py`
2. Add the URL pattern to `blog/urls.py`
3. Create the template in `templates/blog/`
4. Extend `base.html` — never duplicate the nav/footer

## Running Tests

```bash
uv run pytest
uv run pytest -v --tb=short  # verbose
```

## Submitting Changes

1. Branch from `main`
2. Keep PRs focused — one feature or fix per PR
3. Update `USAGE.md` if the change affects how users interact with the app
4. Add an ADR in `docs/adr/` if the change involves a significant architectural decision
