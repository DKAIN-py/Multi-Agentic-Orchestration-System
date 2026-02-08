from typing import Type
from crewai.tools import BaseTool
import os 
from pydantic import BaseModel

from agentops.sdk.decorators import tool as ao_tool



class ListFileInput(BaseModel):
    pass

@ao_tool(name="File listing tool")
class ListFilesTool(BaseTool):
    name: str = "List Files Tool"
    description: str = "Used to list all the avialable files for searching and quering"

    args_schema: Type[BaseModel] = ListFileInput

    def _run(self)->str:
        try:
            file_dir = os.getenv('LOCAL_FILES_DIR')
            if not os.path.exists(file_dir):
                return "Local directery dose not exists\n"
            
            files = [f for f in os.listdir(file_dir) if os.path.isfile(os.path.join(file_dir, f))]

            if not files:
                return f"No files found in the {file_dir}"
            
            return "Available Files:\n" + "\n".join(files)

        except Exception as e:
            return f"Error Listing files: {e}"