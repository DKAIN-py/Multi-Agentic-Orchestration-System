from pydantic import Field, BaseModel
from typing import List

class RecuirementExtracter(BaseModel):
    skills: List[str] = Field(...,description="Skill set required by recuriter")
    experience: str = Field(default="None", description="Experience required for the job")
    domain: str = Field(..., description="Field of work")
    budget: str = Field(default="None", description="Hourly rate of work")
    location: str = Field(default="None", description="location of candidates")
    gender: str = Field(default="Prefer not to say", description="Gender of the candidates")
    age: str = Field(default="22-30", description="Age range of the candidates")