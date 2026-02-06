from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class AgentFile(BaseModel):
    path: str
    file_type: str  
    description: Optional[str] = None 
    
class AgentInput(BaseModel):
    user_id: str          
    session_id: str       
    task_id: str         
    
    content: str          
    
    files: List[AgentFile] = []  
    
    context: Dict[str, Any] = {} 

class AgentOutput(BaseModel):
    status: str           
    
    content: str          
    
    generated_files: List[str] = [] 
    
    metadata: Dict[str, Any] = {}   