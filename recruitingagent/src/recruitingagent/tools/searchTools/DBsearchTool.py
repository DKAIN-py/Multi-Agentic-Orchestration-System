from crewai.tools import BaseTool
from typing import Type, List
from pydantic import BaseModel, Field
import psycopg2
from psycopg2.extras import RealDictCursor
import os

# DATABASE CONFIG
DB_PARAMS = {
    "host" :os.getenv("DB_HOST"), 
    "dbname":os.getenv("DB_NAME"),
    "user":os.getenv("DB_USER"),
    "password":os.getenv("DB_PASSWORD"),
    "port":os.getenv("DB_PORT")
}


class DBsearchToolInput(BaseModel):
    skill_query: List[str] = Field(..., description="skill query to be exceuted")

class DBsearchTool(BaseTool):
    name: str = "Databse searching tool"
    description: str = (
        "used to search for candiates requested by user"
    )
    args_schema: Type[BaseModel] = DBsearchToolInput

    def _run(self, skill_query: list[str]) -> str:
        try:
            conn = psycopg2.connect(**DB_PARAMS)

            if not conn:
                print("Could not connect to database!!")

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = f"SELECT name, bio, profile_link FROM candidates WHERE %s = ANY(skills);"

                cur.execute(query,(skill_query))

                candidate_list = cur.fetchall()

                if not candidate_list:
                    print(f"No records found for skill: {skill_query}")

                output = []
                for row in candidate_list:
                    name = row.get('name','N\A')
                    profile_link = row.get('profile_link','N\A')
                    bio = row.get('bio','N\A')
                    output.append(f"Name: {name} | Profile Link: {profile_link} | Bio: {bio}")

                return '\n'.join(output)
        
        except psycopg2.Error as e:
            print(f"Database Error: {e}")

        finally:
            if conn:
                conn.close()
        

