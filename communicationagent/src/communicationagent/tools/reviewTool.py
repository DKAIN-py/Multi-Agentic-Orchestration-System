from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# class reviewToolInput(BaseModel):
#         sending_signal: bool = Field(default=True, description="Set to False if user says 'directly', 'immediately', 'no review', or 'urgent'. Default is True.")

class ReviewTool(BaseTool):
    name: str = "Asks for human review"
    description: str = (
        "Pauses execution to show the draft to the human and get feedback. "
        "Input: The draft text. Output: The human's feedback."
    )

    def _run(self, draft_msg: str):
        print(f"\n\n--- DRAFT MESSAGE PREVIEW ---\n{draft_msg}\n--------------------------------")
        
        feedback = input("\n[HUMAN]: Type 'ok' to approve, or type your changes here: ")

        return feedback