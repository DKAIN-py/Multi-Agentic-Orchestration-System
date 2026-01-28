from crewai.tools import BaseTool
from typing import Type, List, Any, Dict, Union
from pydantic import BaseModel, Field
import psycopg2
import os
import json
import ast

# DATABASE CONFIG
DB_PARAMS = {
    "host" :os.getenv("DB_HOST"), 
    "dbname":os.getenv("DB_NAME"),
    "user":os.getenv("DB_USER"),
    "password":os.getenv("DB_PASSWORD"),
    "port":os.getenv("DB_PORT")
}

class DBSaverToolInput(BaseModel):
    # name: str = Field(..., description="Full name of the candidate.")
    # link: str = Field(..., description="URL to their LinkedIn profile.")
    # bio: str = Field(..., description="Summary of their profile.")
    # skills: str = Field(..., description="Comma-separated list of skills, e.g., 'Python,Django'.")
    candidateList: Union[str ,List[Dict[str, Any]], Dict[str, Any]] = Field(..., description="A candidate list representing a LIST of candidates objects or a json string.")

class CandidateSaverTool(BaseTool):
    name: str = "Candidate Saver Tool"
    description: str = (
        "Saves a newly found candidate to the local database. "
        "MUST be called for every good candidate found on the web."
    )

    args_schema: Type[BaseModel] = DBSaverToolInput

    def _run(self, candidateList: Union[str ,List[Dict[str, Any]], Dict[str, Any]]) -> str:        # name: str, link: str, bio: str, skills: str
        conn = None
        try:
            candidate_list = []
            
            if isinstance(candidateList, dict):
                parsed_data = candidateList

            elif isinstance(candidateList, list):
                candidate_list = candidateList

            elif isinstance(candidateList, str):
                try:
                    
                    parsed_data = json.loads(candidateList)
                    if isinstance(parsed_data, list):
                        candidate_list = parsed_data
                    elif isinstance(parsed_data, dict):
                        if "candidateList" in parsed_data:
                            candidate_list = parsed_data["candidateList"]
                    else:
                        return f"Error : Recieved unexpected input type {type(candidateList)}\n"
                                
                except json.JSONDecodeError:
                    return "Input is not a valid JSON string.\n"
            
            else:
                return f"Error : Recieved unexpected input type {type(candidateList)}\n"
            
            if not candidate_list:
                return "Input is empty.\n"
            
            conn = psycopg2.connect(**DB_PARAMS)
    
            if not conn:
                print("Could not connect to Database!!")

            print(f"DEBUG: Attempting to save {len(candidate_list)} candidates...")
            with conn.cursor() as cur:
                saved_cout = 0
                skiped_count = 0

                for cand in candidate_list:
                    link = cand.get('profile_link') 
                    name = cand.get('name')

                    raw_skill = cand.get('skills',[])
                    if isinstance(raw_skill,str):
                        skill_list = [s.strip() for s in raw_skill.split(',')]
                    
                    else:
                        skill_list = raw_skill

                    if not link or not name:
                        continue

                    query =  f"""
                            INSERT INTO candidate (name,profile_link,skills,bio,platform)
                            VALUES (%s,%s,%s,%s,'LinkedIn')
                            RETURNING id;   
                            """

                    try:
                        cur.execute(query,((name, link, skill_list,cand.get('bio', ''))))
                        if cur.fetchone():
                            saved_cout+=1
                        print(f"Saved candidate {name}\n")
                    except psycopg2.Error as e:
                        conn.rollback()
                        skiped_count+=1
                        print(f"Skipped candidate or error {e}\n")

                conn.commit()
                return f"Successfully saved {saved_cout} and Skiped {skiped_count} candidates to the database."
            
        except psycopg2.Error as e:
            print(f"Database Error: {e}")

        finally:
            if conn:
                conn.close()