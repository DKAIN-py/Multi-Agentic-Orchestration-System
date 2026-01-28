from crewai.tools import BaseTool
from typing import BaseModel, Field, Type

class FileSeprationInput(BaseModel):
    filename: str = Field(...,description="Name of the file")

class FileSepration(BaseTool):
    name: str = "File Sepration Tool"
    description: str = {
        "Used to seperate files into one of the three categories for further processing",
        "Seprates file based on there extensions into either, Text based, PDFs or Images"
    }

    args_schema: Type[BaseModel] = FileSeprationInput

    def _run(self, filename: str) -> str:
        file_extension_map = {
            "documents": [
                ".pdf", ".docx", ".doc", ".txt", ".rtf", ".odt", ".epub", ".md"
            ],
            "data_spreadsheets": [
                ".csv", ".xlsx", ".xls", ".json", ".xml", ".yaml", ".yml", ".tsv", ".sql"
            ],
            "images_ocr": [
                ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp", ".heic"
            ],
            "archives": [
                ".zip", ".tar", ".gz", ".rar", ".7z"
            ],
            "code": [
                ".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".php", ".rb", ".go", ".ts"
            ]
        }

        