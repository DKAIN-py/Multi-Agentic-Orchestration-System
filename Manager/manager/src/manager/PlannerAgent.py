from crewai.agent import Agent
from crewai.task import Task
from crewai.crew import Crew
from pydantic import BaseModel, Field, List, Dict
from crewai.llm import LLM
import os

local_llm = LLM(
    model=os.getenv("OPENAI_MODEL_NAME"),
    base_url=os.getenv("OPENAI_API_BASE"),
    temperature=0.0
)

class PlannerInput(BaseModel):
    prompt: str = Field(...,description="Query of user to be resolved.")

class PlannerOutput(BaseModel):
    plan: List[Dict[str,str]] = Field(..., description="List of agents's tasks for a specific user query.")


class PlannerAgent:

    @staticmethod
    def Planner_Agent():
        Agent(
            role="",
            goal="",
            backstory="",
            max_rpm=5,
            max_iter=3,
            verbose=True,
        )

    @classmethod
    def PlannerTask(cls, query: str) -> List[Dict[str,str]]:
        agent = cls.Planner_Agent()

        task = Task(
            description="",
            output_pydantic=PlannerOutput,
            agent=agent
        )

        result = Crew(agents=[agent], tasks=[task]).kickoff()
        return result.pydantic.plan