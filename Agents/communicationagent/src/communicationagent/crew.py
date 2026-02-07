# Crewai imports
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task
from crewai import Agent, Crew, Process, Task, LLM

# Pydantic models
from pyModels.extracter import InfoExtracter

# Task Tools
from tools.whatsappTool import SendWhatsAppTool
from tools.emailTool import SendEmailTool
from tools.reviewTool import ReviewTool
from tools.dbSearch import dbSearchTool

# Monitoring
from agentops.sdk.decorators import agent as ao_agent, task as ao_task

# utils
from typing import List
import os


dbsearch = dbSearchTool()
sendEmail = SendEmailTool()
sendwhatsapp = SendWhatsAppTool()
reviewSignal = ReviewTool()

local_llm = LLM(
    model=os.getenv("OPENAI_MODEL_NAME"),
    base_url=os.getenv("OPENAI_API_BASE"),
    temperature=0.0
)

@ao_agent(name="Communication Agent")
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
            verbose=True,
            llm=local_llm
        )
    
    @agent
    def contact_info(self) -> Agent:
        return Agent(
            config=self.agents_config['contact_info'],
            tools=[dbsearch],
            max_rpm = 5,
            max_iter=3,
            verbose=True,
            llm=local_llm
        )
    
    @agent
    def content_gen(self) -> Agent:
        return Agent(
            config=self.agents_config['content_gen'],
            max_rpm = 5,
            max_iter=3,
            verbose=True,
            llm=local_llm
        )
    
    @agent
    def content_verifi(self) -> Agent:
        return Agent(
            config=self.agents_config['content_verifi'],
            tools=[reviewSignal],
            max_rpm = 5,
            max_iter=3,
            verbose=True,
            llm=local_llm
        )

    @agent
    def send_output(self) -> Agent:
        return Agent(
            config=self.agents_config['send_output'],
            tools=[sendEmail,sendwhatsapp],
            max_rpm = 5,
            max_iter=3,
            verbose=True,
            llm=local_llm
        )

    @ao_task(name="Fields extracting")
    @task
    def extracting_task(self) -> Task:
        return Task(
            config=self.tasks_config['extracting'],
            output_pydantic=InfoExtracter
        )

    @ao_task(name="Retriving contact information from DB")
    @task
    def contact_info_task(self) -> Task :
        return Task(
            config=self.tasks_config['contact_info'],
            expected_output="Name,email and phone only",
            context=[self.extracting_task()]
        )
    
    @ao_task(name="Generating message/email to send")
    @task
    def content_gen_task(self) -> Task :
        return Task(
            config=self.tasks_config['content_gen_task'],
            context=[self.extracting_task(), self.contact_info_task()]
        )
    
    @ao_task(name="Verifying Content before sending(HITL)")
    @task
    def content_verifi_task(self) -> Task:
        return Task(
            config=self.tasks_config['content_verifi_task'],
            context=[self.content_gen_task(), self.extracting_task()],
            human_input=True
        )

    @ao_task(name="Sending Ouptut") 
    @task
    def sending_output(self) -> Task:
        return Task(
            config=self.tasks_config['sending_output'],
            context=[self.extracting_task() ,self.contact_info_task() ,self.content_verifi_task()]
        )

    @crew
    async def crew(self) -> Crew:

        return await Crew(
            agents=self.agents, 
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,
        )
