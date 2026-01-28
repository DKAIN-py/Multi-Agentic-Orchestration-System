from crewai import Agent, Crew, Process, Task, LLM
from langchain_ollama import OllamaLLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from pymodels.recuirementExtracter import RecuirementExtracter
from pymodels.webSearchOutput import CandidateList
from tools.DBSaverTool import CandidateSaverTool
from tools.searchTools.DBsearchTool import DBsearchTool, checkDBRes
from tools.searchTools.WebsearchTool import WebSearchTool, search_web
import os

customSearch = WebSearchTool()
dbsearch = DBsearchTool()
candidateSaver = CandidateSaverTool()

local_llm = LLM(
    model=os.getenv("OPENAI_MODEL_NAME"),
    base_url=os.getenv("OPENAI_API_BASE"),
    temperature=0.0
)


@CrewBase
class Recruitingagent():
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
            tools=[dbsearch],
            max_iter=10,
            llm=local_llm,
            verbose=True,
        )

    @agent
    def CandidateFinder(self) -> Agent:
        return Agent(
            config=self.agents_config['CandidateFinder'],
            tools=[customSearch],
            max_iter=10,
            llm=local_llm,
            verbose=True,
            #allow_delegation=False
        )
    
    @agent
    def CandidateSaver(self) -> Agent:
        return Agent(
            config=self.agents_config['CandidateSaver'],
            tools=[candidateSaver],
            max_iter=10,
            llm=local_llm,
            verbose=True
        )

    @task
    def RecurimentExtracter_task(self) -> Task:
        return Task(
            config=self.tasks_config['RecurimentExtracter_task'],
            output_pydantic=RecuirementExtracter
        )

    @task 
    def DBcandidate_search_task(self) -> Task:
        return Task(
            config=self.tasks_config['DBcandidate_search_task'],
            context=[self.RecurimentExtracter_task()],
            callback=checkDBRes
        )

    @task
    def candidate_finding_task(self) -> Task:
        return Task(
            config=self.tasks_config['candidate_finding_task'],
            context=[self.DBcandidate_search_task(),self.RecurimentExtracter_task()],
            conditional=search_web,
            output_pydantic=CandidateList
        )

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
