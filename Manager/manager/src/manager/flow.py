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
from IO import AgentInput, AgentOutput
import os


agentops.init(
    api_key=os.getenv('AGENT_OPS_API_KEY'), 
    skip_auto_end_session=True,
)

class ManagerState(BaseModel):
    request: AgentInput = Field(...,description="Full input packet given by server")
    plan: List[Dict[str,str]] = Field(..., description="List of Key value pair of agent and task, where key is agent and value is task for a specific user query.")
    current_step_idx: int = Field(default=0, description="Index of task currently being exceuted.")
    exceution_history: List[str] = Field(default=[], description="Accumulated results from the agents")
    trace_context: agentops.start_trace = Field(default=Any, description="Used to track each session of Manager and System")


class Manager(Flow[ManagerState]):

    @start
    async def initialize(self, payload: AgentInput):
        print(f"Task started for {payload.task_id}")
        self.state.request = payload

        self.state.trace_context = agentops.start_trace(
            name=f"Kins-Manager-{payload.session_id}",
            tags=["production", payload.user_id]
        )

        planner_prompt = payload.content
        if payload.files:
            file_desc = ",".join([f"Path: {f.path}, Description: {f.description}" for f in payload.files])
            planner_prompt += f"\n(User has attached: {file_desc})"
        
        self.state.plan = await PlannerAgent.PlannerTask(planner_prompt)
        
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

        context_str = "\n".join(self.state.exceution_history)

        file_str =""
        if self.state.request.files:
            file_str = "\nAVAILABLE FILES:\n" + "\n".join(
                [f"- {f.path} ({f.description})" for f in self.state.request.files]
            )

        curr_input = (
            f"**OBJECTIVE** : {current_subquery}\n\n"
            f"**CONTEXT FROM PREVIOUS STEPS: {context_str}\n\n**"
            f"{file_str}"
        )
        
        try:
            if isinstance(selected_crew, Crew):
                result = await selected_crew.crew().akickoff(input={"content" : curr_input})
            elif isinstance(selected_crew, Flow):
                result = await selected_crew.akickoff(input={"data" : curr_input})

            output = str(result)

            self.state.trace_context.span.set_attribute(f"step_{self.state.current_step_idx}_output", output)
            self.state.exceution_history.append(f"Result From: {current_crew}: {output}")
            self.state.current_step_idx += 1

            return "process_next_step"

        except Exception as e:
            agentops.end_trace(self.state.trace_context, end_state=TraceState.ERROR)
            raise e
        
@listen("Complete")
def finalize(self):
    agentops.end_trace(self.state.trac_context, end_state=TraceState.SUCCESS)

    final_content = self.state.exceution_history[-1] if self.state.exceution_history else "No output generated"

    return AgentOutput(
        status="Success",
        content=final_content,
        metadata={
            "steps exceuted":self.state.current_step_idx,
            "plan":self.state.plan 
        }
    )
        
    
