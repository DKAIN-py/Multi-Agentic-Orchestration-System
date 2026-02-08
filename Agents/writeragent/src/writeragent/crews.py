# Crewai imports
from crewai.project import CrewBase, agent, crew, task
from crewai import Agent, Crew, Process, Task, LLM

# Task Tools
from .tools.ExcelFileTool import ExcelFileWritingTool
from .tools.DOCXFileTool import DOCXFileWritingTool
from .tools.TextFileTool import TextFileWritingTool
from .tools.PDFFileTool import PDFFileWritingTool

# Monitoring
from agentops import task as ao_task

# utils
import os


local_llm = LLM(
    model=os.getenv("OPENAI_MODEL_NAME"),
    base_url=os.getenv("OPENAI_API_BASE"),
    temperature=0.0
)

@ao_task(name="Text file creation")
@CrewBase
class TextCrew:
    agents_config = 'config/text/agents.yaml'
    tasks_config = 'config/text/tasks.yaml'

    @agent
    def text_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['text_specialist'],
            tools=[TextFileWritingTool()],
            max_rpm=5,
            max_iter=3,
            llm=local_llm,
            verbose=True
        )
    
    @task
    def text_task(self) -> Task:
        return Task(
            config=self.tasks_config['text_task'],
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.text_specialist()],
            tasks=[self.text_task()],
            process=Process.sequential,
            verbose=True 
        )

@ao_task(name="PDF file creation")    
@CrewBase
class PdfCrew:
    """PDF Generation Crew"""
    agents_config = 'config/pdf/agents.yaml'
    tasks_config = 'config/pdf/tasks.yaml'

    @agent
    def pdf_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['pdf_specialist'],
            tools=[PDFFileWritingTool()],
            verbose=True
        )

    @task
    def pdf_task(self) -> Task:
        return Task(
            config=self.tasks_config['pdf_task'],
            agent=self.pdf_specialist()
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.pdf_specialist()],
            tasks=[self.pdf_task()],
            process=Process.sequential,
            verbose=True
        )

@ao_task(name="Excel file creation")
@CrewBase
class ExcelCrew:
    """Excel Data Extraction Crew"""
    agents_config = 'config/excel/agents.yaml'
    tasks_config = 'config/excel/tasks.yaml'

    @agent
    def excel_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['excel_specialist'],
            tools=[ExcelFileWritingTool()],
            verbose=True
        )

    @task
    def excel_task(self) -> Task:
        return Task(
            config=self.tasks_config['excel_task'],
            agent=self.excel_specialist()
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.excel_specialist()],
            tasks=[self.excel_task()],
            process=Process.sequential,
            verbose=True
        )

@ao_task(name="Docx file creation")
@CrewBase
class DocxCrew:
    """Word Document Crew"""
    agents_config = 'config/docx/agents.yaml'
    tasks_config = 'config/docx/tasks.yaml'

    @agent
    def docx_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['docx_specialist'],
            tools=[DOCXFileWritingTool()],
            verbose=True
        )

    @task
    def docx_task(self) -> Task:
        return Task(
            config=self.tasks_config['docx_task'],
            agent=self.docx_specialist()
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.docx_specialist()],
            tasks=[self.docx_task()],
            process=Process.sequential,
            verbose=True
        )

