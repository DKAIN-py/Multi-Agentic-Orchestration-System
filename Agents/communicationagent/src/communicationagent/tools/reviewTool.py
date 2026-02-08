from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from agentops.sdk.decorators import tool as ao_tool


class reviewToolInput(BaseModel):
        sending_signal: bool = Field(default=True, description="Set to False if user says 'directly', 'immediately', 'no review', or 'urgent'. Default is True.")
        draft_msg: str = Field(...,description="Last updated message or email")

@ao_tool(name="HITL Tool for communication serivce")
class ReviewTool(BaseTool):
    name: str = "Asks for human review"
    description: str = (
        "Pauses execution to show the draft to the human and get feedback. "
        "Input: The draft text. Output: The human's feedback."
    )

    args_schema: Type[BaseModel] = reviewToolInput

    def _run(self,sending_signal: bool,draft_msg: str):
        if sending_signal:
            print(f"\n\n--- DRAFT MESSAGE PREVIEW ---\n{draft_msg}\n--------------------------------")
    
        feedback = input("\n[HUMAN]: Type 'ok' to approve, or type your changes here: ")

        return feedback