from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import os


from agentops.sdk.decorators import tool as ao_tool


class FileWritingInput(BaseModel):
    content: str = Field(...,description="Formatted content to be written in a file")
    filename: str = Field(...,description="A dummy filename created by agent in refrence to the content")

@ao_tool(name="Text Tool")
class TextFileWritingTool(BaseTool):
    name: str = "Textual File Writing Tool"
    description: str = "Used to create files from the formatted content sent by user"

    args_schema: Type[BaseModel] = FileWritingInput

    def _run(self, content: str, filename: str) -> str:
        path = os.getenv('WRITTEN_PATH')
        
        try:
            
            if filename.endswith('.txt'):
                filename = os.path.join(path,filename)
                with open(filename, "w") as f:
                    f.write(content)
                
                return f"Successfull file creation at {filename}"

            elif filename.endswith('.md'):
                filename = os.path.join(path,filename)
                with open(filename, "w") as f:
                    f.write(content)
                return f"Successfull file creation at {filename}"
            
            else:
                return f"File type not defined  : {filename.strip().split('.')[-1]}"
            
        except Exception as e:
            return f"Error occured during file selection: {e}"