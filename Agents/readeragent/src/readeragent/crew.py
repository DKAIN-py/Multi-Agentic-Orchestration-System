# Crewai imports
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task
from crewai import Agent, Crew, Process, Task, LLM

# Tasl tools
from .tools.UniversalParserTool import UniversalParserTool
from .tools.ListFilesTool import ListFilesTool
from .tools.QuesAnswTool import QuesAnswTool

# Monitoring
from agentops.sdk.decorators import agent as ao_agent, task as ao_task

# utils
from typing import List
import os





local_llm = LLM(
    model=os.getenv("OPENAI_MODEL_NAME"),
    base_url=os.getenv("OPENAI_API_BASE"),
    temperature=0.0
)

@ao_agent(name="Reader Agent")
@CrewBase
class Readeragent():

    agents: List[BaseAgent]
    tasks: List[Task]


    @agent
    def knowledge_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['knowledge_manager'],
            llm=local_llm,
            tools=[UniversalParserTool()],
            max_rpm=5,
            max_iter=3,
            verbose=True
        )

    @agent
    def search_planner(self) -> Agent:
        return Agent(
            config=self.agents_config['search_planner'],
            llm=local_llm,
            tools=[ListFilesTool()],
            max_rpm=5,
            max_iter=3,
            verbose=True
        )

    @agent
    def data_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['data_analyst'],
            llm=local_llm,
            tools=[QuesAnswTool()],
            max_rpm=5,
            max_iter=3,
            verbose=True
        )

    @ao_task(name="Parsing input")
    @task
    def ingestion_task(self) -> Task:
        return Task(
            config=self.tasks_config['ingestion_task'],
        )

    @ao_task(name="Finding right docs")
    @task
    def search_planning_task(self) -> Task:
        return Task(
            config=self.tasks_config['search_planning_task'],
            context=[self.ingestion_task()]
        )

    @ao_task(name="Answering user's query")
    @task
    def qa_task(self) -> Task:
        return Task(
            config=self.tasks_config['qa_task'],
            context=[self.search_planning_task()]
        )


    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents, 
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,
        )