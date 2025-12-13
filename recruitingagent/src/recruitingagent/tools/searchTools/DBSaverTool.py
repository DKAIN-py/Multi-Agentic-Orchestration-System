from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import json

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
    candidates_json: str = Field(..., description="A JSON string representing a LIST of candidates. Example: '[{\"name\": \"Alice\", \"link\": \"...\", \"bio\": \"...\", \"skills\": \"Python\"}, {...}]'")

class CandidateSaverTool(BaseTool):
    name: str = "Candidate Saver Tool"
    description: str = (
        "Saves a newly found candidate to the local database. "
        "MUST be called for every good candidate found on the web."
    )

    args_schema: Type[BaseModel] = DBSaverToolInput

    def _run(self, candidates_json) -> str:        # name: str, link: str, bio: str, skills: str
        try:
            candidate_list = json.loads(candidates_json)
            conn = psycopg2.connect(**DB_PARAMS)
    
            if not conn:
                print("Could not connect to Database!!")
    
            with conn.cursor() as cur:
                saved_cout = 0
                for cand in candidate_list:
                    raw_skill = cand.get('skills',[])
                    if isinstance(raw_skill,str):
                        skill_list = [s.strip() for s in raw_skill.split(',')]
                    
                    else:
                        skill_list = raw_skill

                    query =  f"""
                            INSERT INTO candidate (name,profile_link,skills,bio,platform)
                            VALUES (%s,%s,%s,%s,'LinkedIn') 
                            ON CONFLICT (profile_link) DO NOTHING;   
                            """
                
                    cur.execute(query,((cand.get('name'), cand.get('link') or cand.get('profile_link'), skill_list,cand.get('bio'))))

                    saved_cout+=1

                conn.commit()
                return f"Successfully saved {saved_cout} candidates to the database."
        
        except json.JSONDecodeError as j:
            print(f"Json decoder Error: {j}")
            
        except psycopg2.Error as e:
            print(f"Database Error: {e}")

        finally:
            if conn:
                conn.close()