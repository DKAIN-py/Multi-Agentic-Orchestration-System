from pydantic import Field, BaseModel
from typing import List

class InfoExtracter(BaseModel):
    names: List[str] = Field(...,description="Name of the person")
    content: str = Field(...,description="Content on which email/message to be written")
    typeof: str = Field(..., description="Type of person to search for, Client or Employee. This will be resolved by what CSV file is being used for searching.")
    tone: str = Field(default="Formal and Corporate like",description="Tone of the message/email to be written")
    msgtype: str = Field(default="email", description="What kind of message to written, email, SMS, simple message")
    sending_signal: bool = Field(default=True, description="Set to False if user says 'directly', 'immediately', 'no review', or 'urgent'. Default is True.")