from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class AgentFile(BaseModel):
    path: str  
    description: Optional[str] = None 
    
class AgentInput(BaseModel):

    user_id: str = "default_user"         
    session_id: str = "testing_session"      
    task_id: str = "testing_task"        
    
    content: str          
    
    files: List[AgentFile] = []  
    
    context: Dict[str, Any] = {} 

class AgentOutput(BaseModel):
    status: str           
    
    content: str          
    
    generated_files: List[str] = [] 
    
    metadata: Dict[str, Any] = {}   