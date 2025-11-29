from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from tools.custom_tool import CSVSearchTool
from tools.emailTool import SendEmailTool
from tools.whatsappTool import SendWhatsAppTool
from pyModels.extracter import InfoExtracter
from dotenv import load_dotenv

load_dotenv()

csvsearch = CSVSearchTool()
sendEmail = SendEmailTool()
sendwhatsapp = SendWhatsAppTool()

@CrewBase
class Communicationagent():
    """Communicationagent crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def info_extracter(self) -> Agent:
        return Agent(
            config=self.agents_config['info_extracter'],
            verbose=True
        )
    
    @agent
    def contact_info(self) -> Agent:
        return Agent(
            config=self.agents_config['contact_info'],
            tools=[csvsearch],
            verbose=True
        )
    
    @agent
    def content_gen(self) -> Agent:
        return Agent(
            config=self.agents_config['content_gen'],
            verbose=True
        )
    
    @agent
    def send_output(self) -> Agent:
        return Agent(
            config=self.agents_config['send_output'],
            tools=[sendEmail,sendwhatsapp],
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
    def sending_output(self) -> Task:
        return Task(
            config=self.tasks_config['sending_output'],
            context=[self.extracting_task() ,self.contact_info_task() ,self.content_gen_task()]
        )

    @crew
    def crew(self) -> Crew:

        return Crew(
            agents=self.agents, 
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,
        )
