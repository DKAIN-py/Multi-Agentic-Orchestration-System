from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from tools.dbSearch import dbSearchTool
from tools.emailTool import SendEmailTool
from tools.whatsappTool import SendWhatsAppTool
from tools.reviewTool import ReviewTool
from pyModels.extracter import InfoExtracter

dbsearch = dbSearchTool()
sendEmail = SendEmailTool()
sendwhatsapp = SendWhatsAppTool()
reviewSignal = ReviewTool()


@CrewBase
class Communicationagent():
    """Communicationagent crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def info_extracter(self) -> Agent:
        return Agent(
            config=self.agents_config['info_extracter'],
            max_rpm = 5,
            max_iter=3,
            verbose=True
        )
    
    @agent
    def contact_info(self) -> Agent:
        return Agent(
            config=self.agents_config['contact_info'],
            tools=[dbsearch],
            max_rpm = 5,
            max_iter=3,
            verbose=True
        )
    
    @agent
    def content_gen(self) -> Agent:
        return Agent(
            config=self.agents_config['content_gen'],
            max_rpm = 5,
            max_iter=3,
            verbose=True
        )
    
    @agent
    def content_verifi(self) -> Agent:
        return Agent(
            config=self.agents_config['content_verifi'],
            tools=[reviewSignal],
            max_rpm = 5,
            max_iter=3,
            verbose=True
        )

    @agent
    def send_output(self) -> Agent:
        return Agent(
            config=self.agents_config['send_output'],
            tools=[sendEmail,sendwhatsapp],
            max_rpm = 5,
            max_iter=3,
            verbose=True
        )


    @task
    def extracting_task(self) -> Task:
        return Task(
            config=self.tasks_config['extracting'],
            output_pydantic=InfoExtracter
        )

    @task
    def contact_info_task(self) -> Task :
        return Task(
            config=self.tasks_config['contact_info'],
            expected_output="Name,email and ohone only",
            context=[self.extracting_task()]
        )
    
    @task
    def content_gen_task(self) -> Task :
        return Task(
            config=self.tasks_config['content_gen_task'],
            context=[self.extracting_task(), self.contact_info_task()]
        )
    
    @task
    def content_verifi_task(self) -> Task:
        return Task(
            config=self.tasks_config['content_verifi_task'],
            context=[self.content_gen_task(), self.extracting_task()],
            human_input=True
        )

    @task
    def sending_output(self) -> Task:
        return Task(
            config=self.tasks_config['sending_output'],
            context=[self.extracting_task() ,self.contact_info_task() ,self.content_verifi_task()]
        )

    @crew
    def crew(self) -> Crew:

        return Crew(
            agents=self.agents, 
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,
        )
