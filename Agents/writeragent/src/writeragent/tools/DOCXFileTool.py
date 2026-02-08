from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import os
import pypandoc
from agentops.sdk.decorators import tool as ao_tool


class FileWritingInput(BaseModel):
    content: str = Field(...,description="Formatted content to be written in a docx file")
    filename: str = Field(...,description="A dummy filename created by agent in refrence to the content")

@ao_tool(name="DOCX Tool")
class DOCXFileWritingTool(BaseTool):
    name: str = "Docx File Writing Tool"
    description: str = "Used to create files from the formatted content sent by user"

    args_schema: Type[BaseModel] = FileWritingInput

    def _run(self, content: str, filename: str) -> str:
        path = os.getenv('WRITTEN_PATH')
        
        try:
            
            style_path = os.getenv('STYLE_PATH_DOCX')
            filename = os.path.join(path,filename)

            temp_md_path = os.path.join(path, "temp_input.md")

            with open(temp_md_path, 'w', encoding="utf-8") as f:
                f.write(content)

            output = pypandoc.convert_file(
                source_file=temp_md_path,
                to='docx',
                format='md',
                outputfile=filename,
                extra_args=[
                    '--standalone',
                    f'--reference-doc={style_path}'
                ]
            )

            return f"Successfully created DOCX at {filename}"
            
        except Exception as e:
            return f"Error occured during file selection: {e}"