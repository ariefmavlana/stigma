from crewai.project import CrewBase, agent, task, crew
from crewai import Agent, Crew, Process, Task
import os

@CrewBase
class TestCrew:
    agents_config = "config/agents_en.yaml"
    tasks_config = "config/tasks_en.yaml"

    def __init__(self, language="English"):
        if language == "id":
            self.agents_config = "config/agents_id.yaml"
            self.tasks_config = "config/tasks_id.yaml"

    @agent
    def topic_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["topic_researcher"],
            llm="groq/llama3-8b-8192",  # fake
        )

c = TestCrew(language="id")
print("Agent config loaded:", list(c.agents_config.keys()) if isinstance(c.agents_config, dict) else c.agents_config)
