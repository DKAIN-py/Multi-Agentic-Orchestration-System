# Crewai imports
from crews import Communicationagent, Readeragent, Recruitingagent, FileGenerationFlow
from crewai.flow.flow import Flow, start, listen, router
from crewai.crew import Crew

# Pydantic models
from pydantic import BaseModel, List, Field, Dict, Any
from PlannerAgent import PlannerAgent

# Monitoring
from agentops import TraceState
import agentops

# utils
import os


agentops.init(
    api_key=os.getenv('AGENT_OPS_API_KEY'), 
    skip_auto_end_session=True,
)

class ManagerState(BaseModel):
    user_prompt: str = Field(...,description="Prompt given by the user")
    plan: List[Dict[str,str]] = Field(..., description="List of Key value pair of agent and task, where key is agent and value is task for a specific user query.")
    current_step_idx: int = Field(default=0, description="Index of task currently being exceuted.")
    last_output: str = Field(default="", description="Output of a agent after its task exceution finised, to be passed to next agent.")
    trace_context: agentops.start_trace = Field(default=Any, description="Used to track each session of Manager and System")


class Manager(Flow[ManagerState]):

    @start
    async def initialize(self, query):
        self.state.trace_context = agentops.start_trace(
            api_key=os.getenv('AGENT_OPS_API_KEY'), 
            skip_auto_end_session=True,
            name=f"Kins-Manager-{self.state.id}",
            tags=["production","multi-user"]
        )

        query = self.state.user_prompt
        self.state.plan = await PlannerAgent.PlannerTask(query)
        
    @router(initialize, "process_next_step")
    def control_struct(self):

        if self.state.current_step_idx < len(self.state.plan):
            return "exceute_crew" 
        else:
            
            return "Complete"
        
    @listen("exceute_crew")
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

        curr_input = f"Context: {self.state.last_output}\nTask: {current_subquery}" # ALL INPUT AND OUTPUT SHOULD BE OF THIS ORDER
        
        try:
            if isinstance(selected_crew, Crew):
                result = await selected_crew.crew().akickoff(input={"content" : curr_input})
            elif isinstance(selected_crew, Flow):
                result = await selected_crew.akickoff(input={"data" : curr_input})

            self.state.trace_context.span.set_attribute("current_crew", current_crew)
            
            self.state.last_output = str(result)
            self.state.current_step_idx += 1

            return "process_next_step"

        except Exception as e:
            agentops.end_trace(self.state.trace_context, end_state=TraceState.ERROR)
            raise e
        
@listen("Complete")
def finalize(self):
    agentops.end_trace(self.state.trac_context, end_state=TraceState.SUCCESS)
        
    
