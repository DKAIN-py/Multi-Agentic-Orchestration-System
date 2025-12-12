from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import psycopg2
from psycopg2.extras import RealDictCursor

class dbSearchInput(BaseModel):
    """Input schema for dbSearchTool."""
    name: str = Field(..., description="Name of the person to search for")
    typeof: str = Field(..., description="Type of person to search for, Client or Employee.")

class dbSearchTool(BaseTool):
    name: str = "Database Search Tool"
    description: str = (
        "This tool is used to search for email and phone number in Company's database."
    )
    args_schema: Type[BaseModel] = dbSearchInput

    
    def _run(self, name: str, typeof: str) -> str:
        conn = None
        
        try:
            conn = psycopg2.connect(host="localhost", dbname="kins",user="postgres",password="post00",port=5432)

            if conn==False:
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
                    n = row.get('name','N/A')
                    e = row.get('email','N/A')
                    p = row.get('phone','N/A')
                    output.append(f"Name: {n} | Email: {e} | Phone: {p}")
                
                return '\n'.join(output)

        except psycopg2.Error as e:
            print(f"Database Error: {e}")
            
        finally:
            if conn:
                conn.close()



