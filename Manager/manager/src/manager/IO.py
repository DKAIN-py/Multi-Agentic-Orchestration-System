from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class AgentFile(BaseModel):
    path: str  
    description: Optional[str] = None 
    
class AgentInput(BaseModel):

    user_id: str = "default_user"         
    session_id: str = "testing_session"      
    task_id: str = "testing_task"        
    
    content: str  = ""  
    
    files: List[AgentFile] = Field(default_factory=list)
    
    context: Dict[str, Any] = Field(default_factory=dict)

class AgentOutput(BaseModel):
    status: str           
    
    content: str          
    
    generated_files: List[str] = Field(default_factory=list)
    
    metadata: Dict[str, Any] = Field(default_factory=dict)