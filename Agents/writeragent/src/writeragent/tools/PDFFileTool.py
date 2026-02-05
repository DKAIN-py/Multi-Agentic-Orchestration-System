from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import os
import pypandoc
import markdown
from weasyprint import HTML, CSS

class FileWritingInput(BaseModel):
    content: str = Field(...,description="Formatted content to be written in a PDF file")
    filename: str = Field(...,description="A dummy filename created by agent in refrence to the content")

class PDFFileWritingTool(BaseTool):
    name: str = "PDF File Writing Tool"
    description: str = "Used to create files from the formatted content sent by user"

    args_schema: Type[BaseModel] = FileWritingInput

    def _run(self, content: str, filename: str) -> str:
        path = os.getenv('WRITTEN_PATH')
        
        try:
            clean_content = self._sanitize_content(content)

            html_body = markdown.markdown(clean_content, extensions=['tables', 'fenced_code'])

            css_path = os.getenv('CSS_PATH')
            stylesheets = []

            if os.path.exists(css_path):
                stylesheets.append(CSS(filename=css_path))
            else:
                stylesheets.append(CSS(string="table { border: 1px solid black; }"))

            if not os.path.exists(path):
                os.makedirs(path)

            file_path = os.path.join(path,filename)
            
            HTML(string=html_body, base_url=path).write_pdf(file_path, stylesheets=stylesheets)
            return f"PDF created at {file_path}"

            # output = pypandoc.convert_text(
            #     source=content,
            #     to='pdf',
            #     format='md',
            #     outputfile=filename,
            #     extra_args=[
            #         '--pdf-engine=tectonic',
            #         '-V', 'geometry:margin=1in', 
            #         '-V', 'fontsize=11pt',       
            #         '--standalone'
            #     ]
            # )
            
            # print(f"PDF created at {filename}\n")

            # return f"PDF created at {filename}"
            
        except Exception as e:
            return f"Error occured during file selection: {e}"
        

    
    def _sanitize_content(self, text: str) -> str:
        text = text.replace("—", "--").replace("| :–", "| :-")
        
        if text.strip().startswith("title:") and "---" not in text[:20]:
            lines = text.split('\n')
            if len(lines) > 3:
                text = f"---\n{lines[0]}\n{lines[1]}\n---\n" + "\n".join(lines[2:])
        
        return text