"""
STIgma — BlogWriterCrew
────────────────────────
LLM Backend: NVIDIA NIM (OpenAI-compatible endpoint).
Model: moonshotai/kimi-k2-instruct-0905

Performance settings:
  - Single shared LLM instance (built once, used by all agents)
  - verbose=False everywhere (no I/O overhead)
  - max_iter: 3 for all agents (tight cap)
  - max_execution_time: 900s researcher, 600s writer/editor

Agents (sequential):
  1. topic_researcher  — SerperDevTool web search
  2. content_writer    — Markdown draft from research
  3. content_editor    — Polish + SEO + structured JSON output
"""

import os
from functools import lru_cache

from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool

from django.conf import settings


@lru_cache(maxsize=4)
def _build_llm(model_name: str, api_key: str) -> LLM:
    """
    Build a CrewAI LLM instance pointing at NVIDIA NIM.
    lru_cache ensures the same (model, key) combination produces
    exactly one LLM instance for the lifetime of the worker process.
    """
    return LLM(
        model=f"openai/{model_name}",
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key,
        temperature=0.6,
        top_p=0.9,
        max_tokens=4096,
    )


def _get_llm() -> LLM:
    """Resolve config and return a cached LLM instance."""
    api_key = getattr(settings, "NVIDIA_API_KEY", "") or os.getenv("NVIDIA_API_KEY", "")
    if not api_key:
        raise EnvironmentError(
            "NVIDIA_API_KEY is not set. Add it to your .env file.\n"
            "Get a key at https://integrate.api.nvidia.com"
        )
    model_name = getattr(settings, "CREWAI_LLM_MODEL", "meta/llama-3.1-8b-instruct")
    return _build_llm(model_name, api_key)


def _get_search_tool() -> SerperDevTool:
    api_key = getattr(settings, "SERPER_API_KEY", "") or os.getenv("SERPER_API_KEY", "")
    if not api_key:
        raise EnvironmentError(
            "SERPER_API_KEY is not set. Get a free key at https://serper.dev"
        )
    os.environ["SERPER_API_KEY"] = api_key
    return SerperDevTool()


@CrewBase
class BlogWriterCrew:
    """
    Three-agent sequential pipeline: research → write → edit.

    Usage:
        result = BlogWriterCrew().crew().kickoff(inputs={
            "topic": "The Future of Quantum Computing",
            "target_audience": "Curious tech enthusiasts",
            "tone": "Intelligent, engaging, slightly informal",
            "language": "English",
        })
    """

    agents_config = "config/agents_en.yaml"
    tasks_config = "config/tasks_en.yaml"

    @agent
    def topic_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["topic_researcher"],  # type: ignore[index]
            llm=_get_llm(),
            tools=[_get_search_tool()],
            verbose=False,
            max_iter=3,
            max_execution_time=900,
        )

    @agent
    def content_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["content_writer"],  # type: ignore[index]
            llm=_get_llm(),
            verbose=False,
            max_iter=3,
            max_execution_time=600,
        )

    @agent
    def content_editor(self) -> Agent:
        from .tools import SearchBlogTool
        return Agent(
            config=self.agents_config["content_editor"],  # type: ignore[index]
            llm=_get_llm(),
            tools=[SearchBlogTool()],
            verbose=False,
            max_iter=3,
            max_execution_time=600,
        )

    @task
    def research_task(self) -> Task:
        return Task(config=self.tasks_config["research_task"])  # type: ignore[index]

    @task
    def write_task(self) -> Task:
        return Task(config=self.tasks_config["write_task"])  # type: ignore[index]

    @task
    def edit_task(self) -> Task:
        return Task(config=self.tasks_config["edit_task"])  # type: ignore[index]

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=False,
        )


@CrewBase
class BlogWriterCrewID(BlogWriterCrew):
    """
    Indonesian localized instantiation of BlogWriterCrew.
    Inherits all agent/task/crew definitions — only YAML configs differ.
    """
    agents_config = "config/agents_id.yaml"
    tasks_config = "config/tasks_id.yaml"
