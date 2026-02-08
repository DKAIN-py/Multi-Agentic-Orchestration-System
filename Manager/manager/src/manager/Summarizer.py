# Crewai imports
from crewai import Crew ,Agent, Task, LLM

# Pydantic models
from pydantic import BaseModel, Field

# Monitoring
from agentops.sdk.decorators import agent as ao_agent, task as ao_task

# utils
import os

local_llm = LLM(
    model=os.getenv("OPENAI_MODEL_NAME"),
    base_url=os.getenv("OPENAI_API_BASE"),
    temperature=0.0
)


class SummarizeOutput(BaseModel):
    output: str = Field(...,description="Final output")


@ao_agent(name="Summarizing Agent")
class Summarizer:

    @staticmethod
    def SummarizingAgent():
        Agent(
            role="Chief of Staff",
            goal="Provide a high-level summary of the entire operation.",
            backstory="Expert in business reporting and clarity.",
            llm=local_llm,
            max_rpm=5,
            max_iter=3,
            verbose=True
        )   

    @classmethod
    # @ao_task(name="Summarizing Task")
    async def summarizing_task(cls, context: str) -> str:

        agent = cls.SummarizingAgent()

        task = Task(
            description=f"Review the entire execution history of the Kins Manager:\n{context}\n\nDraft a professional executive summary.",
            expected_output="A structured report with 'Objective', 'Key Findings', and 'Action Items'.",
            output_pydantic=SummarizeOutput,
            agent=agent
        )
        res = await Crew(agents=[agent], tasks=[task]).kickoff_async()
        return str(res)