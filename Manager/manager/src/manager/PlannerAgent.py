from agentops.sdk.decorators import agent as ao_agent, task as ao_task
from pydantic import BaseModel, Field, List, Dict
from crewai import Agent, Crew, Task, LLM
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

@ao_agent(name="Planner Agent")
class PlannerAgent:

    @staticmethod
    def Planner_Agent():
        Agent(
            role="Kins System Architect",
            goal="Decompose complex user queries into an optimal sequence of specialized agent tasks.",
            backstory=(
                """You are the master coordinator of the Kins Multi-Agent System.
                Your job is to look at a user request and determine which 'departments' (agents)
                need to be involved. You are highly logical and follow the 'Shortest Path' principle."""
            ),
            max_rpm=5,
            max_iter=3,
            verbose=True,
        )

    @ao_task(name="Planning Task")
    @classmethod
    async def PlannerTask(cls, query: str) -> List[Dict[str,str]]:
        agent = cls.Planner_Agent()

        available_agents = ["communication", "reader", "hiring", "writer"]

        task = Task(
            description=(
                f"Analyze this user query: '{query}'\n\n"
                f"Break it down into an ordered list of steps. For each step, you MUST "
                f"select an agent from this list: {available_agents}.\n"
                "DO NOT invent new agents. Format each step as a dictionary with "
                "the keys 'agent' and 'task' (the specific sub-query for that agent)."
            ),
            expected_output="An ordered JSON list of dictionaries containing 'agent' and 'task'.",
            output_pydantic=PlannerOutput,
            agent=agent
        )

        result = await Crew(agents=[agent], tasks=[task]).akickoff()
        return result.pydantic.plan