from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import warnings

from flow import Manager
import agentops
import asyncio
import os
import nest_asyncio

nest_asyncio.apply()

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
from IO import AgentInput

async def main():

    agentops.init(
    api_key=os.getenv('AGENT_OPS_API_KEY'), 
    skip_auto_end_session=True,
    )

    manager = Manager()

    test_input = AgentInput()

    test_input.content = "find people with 3 years or more experince with java and make a docx of the list and email to our client Divyanshu"

    print(test_input.model_dump())
    # print(type(manager.kickoff(inputs={"request":test_input})))
    result = await manager.kickoff_async(inputs={"request":test_input})
    
    print(result)


if "__main__"==__name__:
    asyncio.run(main())