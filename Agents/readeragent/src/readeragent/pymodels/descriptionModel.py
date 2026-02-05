from pydantic import BaseModel, Field

class DescriptionExtracter(BaseModel):
    description: str = Field(...,description="Information to be retrived from the given document by user")
    filename: str = Field(...,description="name of the file to be processed")
