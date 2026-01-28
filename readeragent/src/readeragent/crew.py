from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from pymodels.descriptionModel import DescriptionExtracter


@CrewBase
class Readeragent():

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def description_extracter(self) -> Agent:
        return Agent(
            config=self.agents_config['description_extracter'],
            max_rpm=5,
            max_iter=3,
            verbose=True
        )

    

    @task
    def description_task(self) -> Task:
        return Task(
            config=self.tasks_config['description_task'],
            output_pydantic=DescriptionExtracter
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents, 
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,
        )