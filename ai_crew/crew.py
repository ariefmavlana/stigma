"""
STIgma — BlogWriterCrew
────────────────────────
LLM Backend: NVIDIA Nemotron via NVIDIA NIM (OpenAI-compatible).
CrewAI uses LiteLLM internally — the "openai/" prefix routes calls
through the OpenAI adapter pointed at NVIDIA's base_url.

Performance settings:
  - reasoning_budget capped at 4096 (was 8192) for faster responses
  - max_tokens 8192 — sufficient for 1200-word posts
  - max_iter: 3 for researcher, 5 for others
  - max_execution_time: 900s for researcher, 600s for others

Agents (sequential):
  1. topic_researcher  — SerperDevTool + WebsiteSearchTool
  2. content_writer    — Markdown draft from research
  3. content_editor    — Polish + SEO + structured JSON output
"""

import os

from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool

from django.conf import settings


def _build_llm() -> LLM:
    """
    Build a CrewAI LLM instance pointing at NVIDIA NIM.
    Optimised for speed: reduced token budgets, no unnecessary retries.
    """
    api_key = getattr(settings, "NVIDIA_API_KEY", "") or os.getenv("NVIDIA_API_KEY", "")
    if not api_key:
        raise EnvironmentError(
            "NVIDIA_API_KEY is not set. Add it to your .env file.\n"
            "Get a key at https://integrate.api.nvidia.com"
        )

    model_name = getattr(
        settings,
        "CREWAI_LLM_MODEL",
        "nvidia/nemotron-3-super-120b-a12b",
    )

    return LLM(
        model=f"openai/{model_name}",
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key,
        temperature=1,
        top_p=0.95,
        max_tokens=4096,
    )


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
        })
    """

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def topic_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["topic_researcher"],  # type: ignore[index]
            llm=_build_llm(),
            tools=[_get_search_tool()],
            verbose=True,
            max_iter=3,              # reduced to 3 for faster research phase
            max_execution_time=900,  # 15-minute cap for research
        )

    @agent
    def content_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["content_writer"],  # type: ignore[index]
            llm=_build_llm(),
            verbose=True,
            max_iter=5,
            max_execution_time=600,
        )

    @agent
    def content_editor(self) -> Agent:
        from .tools import SearchBlogTool
        return Agent(
            config=self.agents_config["content_editor"],  # type: ignore[index]
            llm=_build_llm(),
            tools=[SearchBlogTool()],
            verbose=True,
            max_iter=5,
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
    def crew(self, step_callback=None) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            step_callback=step_callback,
        )
