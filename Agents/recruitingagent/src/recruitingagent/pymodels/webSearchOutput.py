from pydantic import BaseModel, Field
from typing import List

class Candidate(BaseModel):
    name: str = Field(...,description="Name of the candidate")
    profile_link: str = Field(...,description="Link to the candidate's profile")
    bio: str = Field(...,description="Bio of the candidate from their profile")
    skills: List[str] = Field(...,description="List of skills of the candidate")
    match_score: int = Field(...,description="Degree of how much candidate matches the search of user, to be calculated by agent")

class CandidateList(BaseModel):
    candidateList: List[Candidate] = Field(...,description="List of selected candidates")

    