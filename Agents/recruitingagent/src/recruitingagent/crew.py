# Crewai imports
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task
from crewai import Agent, Crew, Process, Task, LLM

# Pydantic models
from .pymodels.recuirementExtracter import RecuirementExtracter
from .pymodels.webSearchOutput import CandidateList

# Task Tools
from .tools.searchTools.WebsearchTool import WebSearchTool, search_web
from .tools.searchTools.DBsearchTool import DBsearchTool, checkDBRes
from .tools.DBSaverTool import CandidateSaverTool

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

@ao_agent(name="Recruting Agent")
@CrewBase
class Recruitingagent:
    """Recruitingagent crew"""

    agents: List[BaseAgent]
    tasks: List[Task]


    @agent
    def RecurimentExtracter(self) -> Agent:
        return Agent(
            config=self.agents_config['RecurimentExtracter'],
            max_iter=10,
            llm=local_llm,
            verbose=True,
        )
    
    @agent
    def DBcandidateSearch(self) -> Agent:
        return Agent(
            config=self.agents_config['DBcandidateSearch'],
            tools=[DBsearchTool()],
            max_iter=10,
            llm=local_llm,
            verbose=True,
        )

    @agent
    def CandidateFinder(self) -> Agent:
        return Agent(
            config=self.agents_config['CandidateFinder'],
            tools=[WebSearchTool()],
            max_iter=10,
            llm=local_llm,
            verbose=True,
            #allow_delegation=False
        )
    
    @agent
    def CandidateSaver(self) -> Agent:
        return Agent(
            config=self.agents_config['CandidateSaver'],
            tools=[CandidateSaverTool()],
            max_iter=10,
            llm=local_llm,
            verbose=True
        )

    @ao_task(name="Conditions extracting")
    @task
    def RecurimentExtracter_task(self) -> Task:
        return Task(
            config=self.tasks_config['RecurimentExtracter_task'],
            output_pydantic=RecuirementExtracter
        )

    @ao_task(name="Database searching for candidate")
    @task 
    def DBcandidate_search_task(self) -> Task:
        return Task(
            config=self.tasks_config['DBcandidate_search_task'],
            context=[self.RecurimentExtracter_task()],
            callback=checkDBRes
        )

    @ao_task(name="Searching for candidates online")
    @task
    def candidate_finding_task(self) -> Task:
        return Task(
            config=self.tasks_config['candidate_finding_task'],
            context=[self.DBcandidate_search_task(),self.RecurimentExtracter_task()],
            conditional=search_web,
            output_pydantic=CandidateList
        )

    @ao_task(name="Saving found candidates to Database")
    @task
    def candidate_saving_task(self) -> Task:
        return Task(
            config=self.tasks_config['candidate_saving_task'],
            context=[self.candidate_finding_task()]
        )

    @crew
    def crew(self) -> Crew:

        return Crew(
            agents=self.agents, 
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,
            memory=False
        )
