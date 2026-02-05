from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import os
import pandas as pd
from io import StringIO
import pypandoc

class FileWritingInput(BaseModel):
    content: str = Field(...,description="Formatted content to be written in a file")
    filename: str = Field(...,description="A dummy filename created by agent in refrence to the content")

class UniversalFileWritingTool(BaseTool):
    name: str = "Universal File Writing Tool"
    description: str = "Used to create files from the formatted content sent by user"

    args_schema: Type[BaseModel] = FileWritingInput

    def _run(self, content: str, filename: str) -> str:
        written_path = os.getenv('WRITTEN_PATH')
        
        try:
            
            if filename.endswith('.txt') or filename.endswith('.md') or filename.endswith('.csv'):
                return self.createTextFile(filename ,content ,written_path)

            elif filename.endswith('.xlsx') or filename.endswith('.xls'):
                return self.createExcelFile(filename ,content ,written_path)
            
            elif filename.endswith('.pdf'):
                return self.createPDF(filename, content, written_path)
            
            elif filename.endswith('.doc') or filename.endswith('.docx'):
                return self.createDOCX(filename, content, written_path)

            else:
                return f"File type is not defined: {filename.strip().split('.')[-1]}"
            
        except Exception as e:
            return f"Error occured during file selection: {e}"


    def createTextFile(self, filename: str ,content: str, path: str) -> str:
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

            elif filename.endswith('.csv'):
                filename = os.path.join(path,filename)
                with open(filename, "w") as f:
                    f.write(content)
                return f"Successfull file creation at {filename}"
            
            else:
                return f"File type not defined  : {filename.strip().split('.')[-1]}"

        except Exception as e:
            return f"Error occured during file creation: {e}"
        
    
    def createExcelFile(self, filename: str ,content: str, path: str):
        try:
            filename = os.path.join(path,filename)
            csv_obj = pd.read_csv(StringIO(content))
            csv_obj.to_excel(filename)

            return f"Successful excel creation at {filename}"

        except Exception as e:
            return f"Error occured during excel creation: {e}"
        

    def createPDF(self, filename: str, content: str, path: str) -> str:
        try:
            filename = os.path.join(path,filename)
            
            output = pypandoc.convert_text(
                source=content,
                to='pdf',
                format='md',
                outputfile=filename,
                extra_args=[
                    '--pdf-engine=tectonic',
                    '-V', 'geometry:margin=1in', 
                    '-V', 'fontsize=11pt',       
                    '--standalone'
                ]
            )
            
            print(f"PDF created at {filename}\n")

            return f"PDF created at {filename}"
        
        except Exception as e:
            return f"Error occured during PDF creation : {e}"
        
    
    def createDOCX(self, filename: str, content: str, path: str) -> str:
        try:
            style_path = '/mnt/windows/Users/Divyanshu/projects/Kins/Agents/writeragent/src/writeragent/pymodels/professional_style.docx'
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
            return f"Error ocurred during DOCX creation: {e}"

        
