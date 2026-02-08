from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import psycopg2
from psycopg2.extras import RealDictCursor
import os

from agentops.sdk.decorators import tool as ao_tool

# DATABASE CONFIG
DB_PARAMS = {
    "host" :os.getenv("DB_HOST"), 
    "dbname":os.getenv("DB_NAME"),
    "user":os.getenv("DB_USER"),
    "password":os.getenv("DB_PASSWORD"),
    "port":os.getenv("DB_PORT")
}

class dbSearchInput(BaseModel):
    """Input schema for dbSearchTool."""
    name: str = Field(..., description="Name of the person to search for")
    typeof: str = Field(..., description="Type of person to search for, Client or Employee.")

@ao_tool(name="DB search Tool")
class dbSearchTool(BaseTool):
    name: str = "Database Search Tool"
    description: str = (
        "This tool is used to search for email and phone number in Company's database."
    )
    args_schema: Type[BaseModel] = dbSearchInput

    
    def _run(self, name: str, typeof: str) -> str:
        conn = None
        
        try:
            conn = psycopg2.connect(**DB_PARAMS)

            if not conn:
                print(f"Could not connect to Database!!")
                conn.close()

            with conn.cursor(cursor_factory=RealDictCursor) as cur:

                tablename = typeof.lower().strip()

                if name.upper() in ['ALL_CLIENTS','ALL_EMPLOYEES','EVERYONE']:
                    query = f"SELECT name,email,phone FROM {tablename};"
                    cur.execute(query)

                else:
                    query = f"SELECT name,email,phone FROM {tablename} WHERE name = ANY(%s);"

                    search_names = [name] if isinstance(name,str) else name

                    cur.execute(query,(search_names,))
                res = cur.fetchall()
                if not res:
                    print(f"No records found for {name} in {tablename}")

                output = []
                for row in res:
                    naam = row.get('name','N/A')
                    emal = row.get('email','N/A')
                    pfone = row.get('phone','N/A')
                    output.append(f"Name: {naam} | Email: {emal} | Phone: {pfone}")
                
                return '\n'.join(output)

        except psycopg2.Error as e:
            print(f"Database Error: {e}")
            
        finally:
            if conn:
                conn.close()



