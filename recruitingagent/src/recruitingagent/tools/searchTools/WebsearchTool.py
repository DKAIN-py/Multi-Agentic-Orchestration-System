from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import json
from googleapiclient.discovery import build
import os 


class WebSearchToolInput(BaseModel):
    search_query: str = Field(...,description="query to search for")

class WebSearchTool(BaseTool):
    name: str = "Google Custom Search Tool"
    description: str = (
        "Searches LinkedIn via Google for NEW candidates. "
        "Use this ONLY if the database search returns no results."
    )

    args_schema: Type[BaseModel] = WebSearchToolInput

    def _run(self, search_query: str) -> str:
        try:
            service = build("customsearch", "v1", developerKey=os.getenv("GOOGLE_API_KEY"))
            linkedin_query = f'site:linkedin.com/in {search_query} -intitle:jobs'

            res = service.cse().list(q=linkedin_query, cx=os.getenv("GOOGLE_CSE_ID"), num=10).execute()

            results = []
            for item in res.get('items',[]):
                candidate =  {
                    "name":item.get('title','').split("-")[0].strip(),
                    "profile_link":item.get('link'),
                    "bio":item.get('snippet','')
                    }
                results.append(candidate)

            return json.dumps(results)
        
        except Exception as e:
            return f"Google Search Error: {str(e)}"
        
def search_web(output):
    return "THRESHOLD NOT MET" in output.raw