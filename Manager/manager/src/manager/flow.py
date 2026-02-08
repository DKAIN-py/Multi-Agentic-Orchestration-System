# Crewai imports
from crews_collection import Communicationagent, Readeragent, Recruitingagent, FileGenerationFlow
from crewai.flow.flow import Flow, start, listen, router
from crewai.crew import Crew

# Pydantic models
from pydantic import BaseModel, Field
from PlannerAgent import PlannerTask

# Monitoring
from agentops import TraceState
import agentops

# utils
from typing import List, Dict, Any, Optional
from IO import AgentInput, AgentOutput
from Summarizer import Summarizer
import os




class ManagerState(BaseModel):
    request: AgentInput = None
    plan: List[Dict[str,str]] = Field(default_factory=list)
    current_step_idx: int = 0
    execution_history: List[str] = Field(default_factory=list)
    trace_context: Optional[Any] = None
    # crews: Dict[str, Any] = None


class Manager(Flow[ManagerState]):

    @start()
    async def initialize(self):
        print(self.state.request.content)
        
        # print(data.get("content"))
        # payload = AgentInput(
        #     user_id=data.get("user_id"),
        #     session_id=data.get("session_id"),
        #     task_id=data.get("task_id"),
        #     content=data.get("content"),
        #     files=data.get("files"),
        #     context=data.get("context")
        # )
        

        # print(payload.content)

        

        payload = self.state.request

        self.state.trace_context = agentops.start_trace(
            tags=["Kins-Manager", payload.user_id]
        )

        planner_prompt = payload.content
        if payload.files:
            file_desc = ",".join([f"Path: {f.path}, Description: {f.description}" for f in payload.files])
            planner_prompt += f"\n(User has attached: {file_desc})"
        
        print(planner_prompt)
        self.state.plan = await PlannerTask(query=planner_prompt)

        # for i in range(len(self.state.plan)):
        #     agent = self.state.plan[i].get("agent")
        #     agent_boj = crew_collection.get(agent)
        #     new_pair = {agent : agent_boj}
        #     self.state.crews.update(new_pair)
    
    @router(initialize)
    def init_struct(self):

        if self.state.current_step_idx < len(self.state.plan):
            return "execute_crew" 
        else:
            
            return "complete"
    
    @listen("execute_crew")
    async def crew_execution(self):

        crew_collection: Dict[str, Crew | Flow] = {
            "communication" : Communicationagent,
            "reader" : Readeragent,
            "hiring" : Recruitingagent,
            "writer" : FileGenerationFlow
        }

        while self.state.current_step_idx < len(self.state.plan):
            step = self.state.plan[self.state.current_step_idx]
            current_crew = step.get("agent")
            current_subquery = step.get("task")

            selected_crew = crew_collection[current_crew]()

            context_str = "\n".join(self.state.execution_history)

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
                    result = await selected_crew.akickoff(inputs={"content" : curr_input})
                elif isinstance(selected_crew, Flow):
                    result = await selected_crew.kickoff_async(inputs={"data" : curr_input})
                else:
                    result = None
                output = str(result)

                self.state.trace_context.span.set_attribute(f"step_{self.state.current_step_idx}_output", output)
                self.state.execution_history.append(f"Result From: {current_crew}: {output}")
                self.state.current_step_idx += 1

                # if self.state.current_step_idx < len(self.state.plan):
                #     return "execute_crew" 
                # else:
                #     return "complete"

            except Exception as e:
                agentops.end_trace(self.state.trace_context, end_state=TraceState.ERROR)
                raise e
        
    
        return "complete"

    @listen("complete")
    async def finalize(self):
        final_str = "\n".join(self.state.execution_history)    
    
        final_content = await Summarizer.summarizing_task(final_str)
    
        agentops.end_trace(self.state.trace_context, end_state=TraceState.SUCCESS)

        output = AgentOutput(
            status="Success",
            content=final_content,
            metadata={
                "steps exceuted":int(self.state.current_step_idx),
                "plan":str(self.state.plan) 
                })

        return output
    
            
            
    
