from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import pandas as pd
import os

class CSVSearchInput(BaseModel):
    """Input schema for MyCustomTool."""
    name: str = Field(..., description="Name of the person to search for")
    typeof: str = Field(..., description="Type of person to search for, Client or Employee. This will be resolved by what CSV file is being used for searching.")

class CSVSearchTool(BaseTool):
    name: str = "CSV file Search Tool"
    description: str = (
        "This tool is used to search for email and phone number in the provided CSV file."
    )
    args_schema: Type[BaseModel] = CSVSearchInput

    def _run(self, name: str, typeof: str) -> str:
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        filename = f"{typeof.lower().strip()}.csv" 
        filename = os.path.join(curr_dir, filename)

        try:
            df = pd.read_csv(filename)
        except FileNotFoundError:
            return f"Error: Could not find file {filename}. Check your folder."

        name_col = 'name'

        if name.upper() in ['ALL_CLIENTS','ALL_EMPLOYEES','EVERYONE']:
            return df[[name_col,'email','phone']].to_string(index=False)

        results = df[df[name_col].str.contains(name, case=False, na=False)]

        if results.empty:
            return f"No record found for '{name}' in {filename}"

        output_data = []
        
        for _, row in results.iterrows():
            email = row.get('email', row.get('internal_email', 'N/A'))
            
            phone = row.get('phone', 'N/A')
            
            output_data.append(f"Name: {row[name_col]}, Email: {email}, Phone: {phone}")

        return "\n".join(output_data)    
