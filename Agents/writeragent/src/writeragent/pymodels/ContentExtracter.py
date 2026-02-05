from pydantic import BaseModel, Field

class ContentExtracter(BaseModel):
    content: str = Field(...,description="Content to be formatted and then writen in the file")
    filename: str = Field(..., description="Dummy name for the file to be created along with appropriate file extension")
