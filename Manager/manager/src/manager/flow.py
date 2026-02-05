from crewai.flow.flow import Flow, start, listen, router
from crews import Communicationagent, Readeragent, Recruitingagent, FileGenerationFlow
from crewai.crew import Crew
from pydantic import BaseModel, List, Field, Dict
from PlannerAgent import PlannerAgent


class ManagerState(BaseModel):
    user_prompt: str = Field(...,description="Prompt given by the user")
    plan: List[Dict[str,str]] = Field(..., description="List of Key value pair of agent and task, where key is agent and value is task for a specific user query.")
    current_step_idx: int = Field(default=0, description="Index of task currently being exceuted.")
    last_output: str = Field(default="", description="Output of a agent after its task exceution finised, to be passed to next agent.")


class Manager(Flow[ManagerState]):

    @start
    async def initialize(self, query):
        query = self.state.user_prompt
        self.state.plan = await PlannerAgent.PlannerTask(query)
        
    @router(initialize)
    def control_struct(self):

        if self.state.current_step_idx < len(self.state.plan):
            return "exceute_crew" 
        else:
            return "Complete"
        
    @listen(control_struct)
    async def crew_exceution(self):

        step = self.state.plan[self.state.current_step_idx]
        current_crew = step.get("agent")
        current_subquery = step.get("task")

        crew_collection: Dict[str, Crew | Flow] = {
            "communication" : Communicationagent(),
            "reader" : Readeragent(),
            "hiring" : Recruitingagent(),
            "writer" : FileGenerationFlow()
        }

        selected_crew = crew_collection[current_crew]

        curr_input = f"Context: {self.state.last_output}\nTask: {current_subquery}"\
        
        try:
            if isinstance(selected_crew, Crew):
                result = await selected_crew.crew().akickoff(input=curr_input)
            elif isinstance(selected_crew, Flow):
                result = await selected_crew.akickoff(input={"data" : curr_input})
        except Exception as e:
            return f"Error occured during crew/flow exceution: {e}" 

        self.state.last_output = str(result)
        self.state.current_step_idx += 1

        return self.control_struct()



