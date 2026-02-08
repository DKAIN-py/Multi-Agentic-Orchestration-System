from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import os
import pandas as pd
from io import StringIO
from agentops.sdk.decorators import tool as ao_tool


class FileWritingInput(BaseModel):
    content: str = Field(...,description="Formatted content to be written in a excel or csv file")
    filename: str = Field(...,description="A dummy filename created by agent in refrence to the content")

@ao_tool(name="Excel Tool")
class ExcelFileWritingTool(BaseTool):
    name: str = "Excel File Writing Tool"
    description: str = "Used to create files from the formatted content sent by user"

    args_schema: Type[BaseModel] = FileWritingInput

    def _run(self, content: str, filename: str) -> str:
        path = os.getenv('WRITTEN_PATH')
        
        try:
            if filename.endswith('.csv'):
                filename = os.path.join(path,filename)
                with open(filename, "w") as f:
                    f.write(content)
                return f"Successfull csv creation at {filename}"
            
            elif filename.endswith('.xlsx') or filename.endswith('.xls'):
            
                filename = os.path.join(path,filename)
                csv_obj = pd.read_csv(StringIO(content))
                csv_obj.to_excel(filename, index=False)
                return f"Successful excel creation at {filename}"
            
            else: 
                return f"File type is not excel or csv, {filename.strip().split('.')[-1]}"
            
        except Exception as e:
            return f"Error occured during file selection: {e}"