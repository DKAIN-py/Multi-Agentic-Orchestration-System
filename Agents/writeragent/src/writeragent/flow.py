# Crewai imports
from crews import PdfCrew, ExcelCrew, DocxCrew, TextCrew
from crewai.flow.flow import Flow, listen, start
from crewai import Agent, Task, Crew

#Monitoring
from agentops import agent as ao_agent


@ao_agent(name="Writer Agent")
class FileGenerationFlow(Flow):
    
    @start()
    def route_request(self):
        print("Analyzing Request...")
        
        router = Agent(
            role='Classifier',
            goal='Classify request as pdf_job, docx_job, or excel_job or text_job or csv_job or markdown_job',
            backstory="You are a logic gate. Output ONLY the tag.",
            allow_delegation=False,
            verbose=True
        )
        
        task = Task(
            description=f"""
            Analyze this input: 
            ---
            {self.state['data']}
            ---
            
            **YOUR STRICT INSTRUCTIONS:**
            1. Ignore the FORMAT of the data inside the input (e.g., if it looks like markdown, json, or csv, IGNORE that).
            2. Look ONLY for the user's explicit command about what file they want to CREATE.
            3. Classify based on the desired OUTPUT:
               - If user mentions "docx", "word", or "doc" -> return 'docx_job'
               - If user mentions "pdf" -> return 'pdf_job'
               - If user mentions "excel", "spreadsheet", "csv" -> return 'excel_job'
               - If user mentions "markdown", "md" -> return 'markdown_job'
               - If user mentions "text", "txt" -> return 'text_job'
            
            Return ONLY the tag.
            """,
            expected_output="One string: 'pdf_job', 'docx_job', 'excel_job', 'csv_job', 'text_job' or markdown_job",
            agent=router
        )
        
        crew = Crew(agents=[router], tasks=[task])
        decision = crew.kickoff().raw.strip().lower()
        
        print(f"Decision: {decision}")
        return decision

    @listen(route_request)
    def execute_specialist(self, decision):
        """Phase 2: The Execution"""
        user_input = self.state['data']
        
        if "excel" in decision or "csv" in decision:
            print("Starting Excel Crew...")
            return ExcelCrew().crew().kickoff(inputs={"data": user_input})
            
        elif "docx" in decision:
            print("Starting Docx Crew...")
            return DocxCrew().crew().kickoff(inputs={"data": user_input})
        
        elif "text" in decision or "markdown" in decision:
            print("Starting Text crew...")
            return TextCrew().crew().kickoff(inputs={"data": user_input})

        elif "pdf" in decision:
            print("Starting PDF Crew...")
            return PdfCrew().crew().kickoff(inputs={"data": user_input})
        
        else:
            return "File type requested is not supported.\n"

