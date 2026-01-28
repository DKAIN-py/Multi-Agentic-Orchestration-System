from pydantic import BaseModel, Field

class DescriptionExtracter(BaseModel):
    information: str = Field(...,description="Information to be retrived from the given document by user")
    rlType: bool = Field(...,description="tells if file is remote (0) or local(1)")
    filename: str = Field(...,description="name of the file to be processed")
