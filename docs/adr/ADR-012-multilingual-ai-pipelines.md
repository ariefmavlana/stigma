# ADR-012: Multi-Lingual AI Pipelines and ReAct Prompt Guardrails

## Status
Accepted

## Date
2026-04-17

## Context
STIgma utilizes CrewAI (`nvidia/nemotron-3-super-120b-a12b`) for generating comprehensive blog post articles encompassing diverse settings: Topics, Audiences, and Tone criteria. As the user base expanded, a requirement evolved: dynamically supporting content generation across multiple languages (e.g., Topic in Indonesian, Target Audience in English) leveraging the same architectural foundations.

During evaluation testing with multi-lingual inputs, three core issues drastically degraded generator performance (`Time to Completion > 5 minutes` and frequent `504 Gateway Timeouts`):
1. **ReAct Translation Overhead:** CrewAI agents use English for logic and role evaluation. Introducing `{language}` and `{topic}` parameters that conflicted with original personas caused excessive "Constraint Conflict". 
2. **Search API Desync:** The `topic_researcher` agent passed strict localized strings directly into `SerperDevTool` while expecting localized outputs but relying on English constraints, leading to sub-optimal tool extraction iterations.
3. **JSON Parser Malfunctions (Silent Retries):** The `content_editor` failed to isolate `{language}` translation mapping outside of JSON schemas. The agent naturally translated JSON *keys* into the target `{language}` or included conversational preambles *(e.g., "Berikut adalah JSON Anda...")*, instantly breaking the strict Python `json.loads()` loop. Consequently, CrewAI repeatedly looped the agent silently in the background up to `max_iter=5`.

## Decision
STIgma transitioned to a **Dual-Configuration Architecture** to fully resolve both logical and parsing faults during multi-lingual processing.

1. **Dual YAML Ecosystem (`_en.yaml` & `_id.yaml`)**: We duplicated and deeply localized the core `agents.yaml` and `tasks.yaml` configurations. This empowers the LLM to execute ReAct loops logically in Bahasa Indonesia when targeted, removing 100% of internal translation delays from the generation process.
2. **Dynamic Class Instantiation (`crew.py`)**: `BlogWriterCrew` is established with the English baseline, while a subclass, `BlogWriterCrewID`, overrides the CrewBase configurations to pull the `_id` YAMLs dynamically based on the input language parameter inside Celery tasks.
3. **Persisted Schema Constraints**: Explicit cross-lingual guardrails remain enforced within both configurations. Particularly inside `tasks_id.yaml`, the Content Editor is explicitly forbidden from generating localized keys or pre-pended prose to guarantee rigid JSON extractability.

## Consequences

### Positive
- **Drastic Speed Increases**: Generating non-English content operates rapidly matching single-language baseline speed.
- **Improved Task Reliability**: Prevention of non-standard JSON generation eradicates background `max_iter` penalty loops causing random server timeouts.
- **Modular Maintenance**: Core Agent personas (`agents.yaml`) and Code definitions (`crew.py`) remain unified conceptually on English standards, eliminating the need to maintain distinct code pipelines per language.

### Negative
- AI Agents consume slightly more context tokens assessing the translation boundary constraints during evaluation.
- Highly obscure languages or complex non-Latin scripts might cause token-splitting lag if relying on smaller LLMs, necessitating model-specific evaluation tests in the future.
