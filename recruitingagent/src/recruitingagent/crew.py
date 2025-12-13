from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from pymodels.recuirementExtracter import RecuirementExtracter
from tools.searchTools.DBSaverTool import CandidateSaverTool
from tools.searchTools.DBsearchTool import DBsearchTool
from tools.searchTools.WebsearchTool import WebSearchTool

customSearch = WebSearchTool()
dbsearch = DBsearchTool()
candidateSaver = CandidateSaverTool()


@CrewBase
class Recruitingagent():
    """Recruitingagent crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def RecurimentExtracter(self) -> Agent:
        return Agent(
            config=self.agents_config['RecurimentExtracter'],
            max_rpm=5,
            max_iter=3,
            verbose=True
        )
    
    @agent
    def CandidateFinder(self) -> Agent:
        return Agent(
            config=self.agents_config['CandidateFinder'],
            tools=[dbsearch,customSearch,candidateSaver],
            max_rpm=5,
            max_iter=3,
            verbose=True
        )

    @task
    def RecurimentExtracter_task(self) -> Task:
        return Task(
            config=self.tasks_config['RecurimentExtracter_task'],
            output_pydantic=RecuirementExtracter
        )

    @task
    def candidate_finding_task(self) -> Task:
        return Task(
            config=self.tasks_config['candidate_finding_task'],
            context=[self.RecurimentExtracter_task()]
        )

    @crew
    def crew(self) -> Crew:

        return Crew(
            agents=self.agents, 
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,
        )
