from crewai.tools import BaseTool
from typing import Type, Optional, List, Dict
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient
import os
import json

class SearchTarget(BaseModel):
    query: str = Field(...,description="Specific question or request from user")
    filter_filename: Optional[str] = Field(None, description="The specific filename to search in. Leave empty to search all.")


class QuesAnswInput(BaseModel):
    targets: List[SearchTarget] = Field(...,description="List of search queries with their related filename")


class QuesAnswTool(BaseTool):
    name: str = "Question Answer Tool"
    description: str = "Used to retreive potential answers from the vector DB to solve user's query"
    
    args_schema: Type[BaseModel] = QuesAnswInput

    def _run(self, targets: List[Dict[str, Optional[str]]]) -> str:
        try:
            qdrant_path = os.getenv('QDRANT_PATH')
            collection_name = os.getenv('COLLECTION_NAME')
            client = QdrantClient(path=qdrant_path)

            retrieved_chunks: list[dict[str,str]] = []
            
            # loading and checking types
            if isinstance(targets, str):
                parsed_target = json.loads(targets)
                if isinstance(parsed_target, dict):
                    if "targets" in parsed_target:
                        targets = parsed_target["targets"]

            elif isinstance(targets, dict):
                if "targets" in parsed_target:
                        targets = parsed_target["targets"]
            
            elif isinstance(targets, list):
                targets = targets

            else:
                return f"Undefined type of input: {type(targets)}"
            
            # main of vector search and answer construction
            for target in targets:
                if isinstance(target, dict):
                    query = target.get('query')
                    filter_filename = target.get('filter_filename')
                else:
                    query = getattr(target, 'query', "")
                    filter_filename = getattr(target, 'filter_filename', None)

                print(f"Query: {query}, Filter name: {filter_filename}")

                chunks = self.get_chunks(client, filter_filename, query, collection_name)

                context = {
                    "Source" : filter_filename if filter_filename else "Genreal Search",
                    "Content" : chunks
                }

                retrieved_chunks.append(context)

            return json.dumps(retrieved_chunks, indent=2)
        
        except Exception as e:
            return f"Error during processing: {e}"
        
    def get_chunks(self ,client: QdrantClient ,filter_filename:str ,query: str, collection_name: str) -> str:
        try:
            if filter_filename:
                clean_filter = os.path.basename(filter_filename)
            else:
                clean_filter = None

            print(f"{filter_filename}\n{clean_filter}")
            
            results = client.query(
                collection_name=collection_name,
                query_text=query,
                limit=50,
            )

            unique_res = []
            seen_content = set()
            for res in results:
                if clean_filter:
                    stored_name = res.metadata.get('source','')

                    if clean_filter not in os.path.basename(stored_name):
                        continue

                content_sign = res.document.strip()[:50]

                if content_sign in seen_content:
                    continue

                seen_content.add(content_sign)
                unique_res.append(res)

                if len(unique_res) >= 10:
                    break 

            results = unique_res
            context = ""
            for res in results:
                src = res.metadata.get('source','Unknown')
                content = res.document.replace("\n"," ").strip()
                context += f"---\nSource: {src}\nContent: {content}\n"

            return context if context else "No relevant information found."

        except Exception as e:
            return f"Error occured: {e}"


