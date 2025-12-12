from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from pymodels.recuirementExtracter import RecuirementExtracter


@CrewBase
class Recruitingagent():
    """Recruitingagent crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def RecurimentExtracter(self) -> Agent:
        return Agent(
            config=self.agents_config['extracter'],
            verbose=True
        )
    

    @task
    def RecurimentExtracter_task(self) -> Task:
        return Task(
            config=self.tasks_config['extracting_task'],
            output_pydantic=RecuirementExtracter
        )


    @crew
    def crew(self) -> Crew:

        return Crew(
            agents=self.agents, 
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,
        )
