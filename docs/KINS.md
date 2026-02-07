# KINS — Technical System Reference

This document is a definitive, file-level reference for the Kins Multi-Agent System (MAS). It explains the Manager (orchestrator), each Agent package (communication, reader, recruiting, writer), the tools they use, the Pydantic data models, and how data flows from the Manager to Agents and back to produced artifacts (`writtenFiles`).

This reference follows the project template structure and maps behavior described in design docs to exact implementation files.

## Overview

Kins is a modular MAS implemented as several small Python packages. The repository contains:

- A Manager flow that receives a single user request and decomposes it into a sequence of agent tasks using a dedicated Planner agent.
- Agent packages under `Agents/` which implement specialized capabilities (communication, reader, recruiting, writer).
- Tools implemented as thin wrappers (Crewai `BaseTool`) for integrations (Qdrant, PostgreSQL, Twilio, SMTP, file converters).
- Minimal Pydantic models under `pymodels/` for strict I/O between tasks.

The Manager delegates ordered tasks to agent crews and/or flows; agents run sequential Task graphs where specific tools are injected and invoked by task configuration.

## Project Structure (key paths)

```
Manager/manager/src/manager/
  PlannerAgent.py
  IO.py
  flow.py
  crews.py

Agents/
  communicationagent/src/communicationagent/
    crew.py
    main.py
    config/agents.yaml
    config/tasks.yaml
    tools/*.py
    pyModels/extracter.py

  readeragent/src/readeragent/
    crew.py
    main.py
    config/agents.yaml
    config/tasks.yaml
    tools/UniversalParserTool.py
    tools/QuesAnswTool.py
    tools/ListFilesTool.py
    pymodels/descriptionModel.py

  recruitingagent/src/recruitingagent/
    crew.py
    main.py
    config/agents.yaml
    config/tasks.yaml
    tools/DBSaverTool.py
    tools/searchTools/DBsearchTool.py
    tools/searchTools/WebsearchTool.py
    pymodels/recuirementExtracter.py
    pymodels/webSearchOutput.py

  writeragent/src/writeragent/
    flow.py
    main.py
    crews.py
    config/{docx,pdf,excel,text}/agents.yaml
    config/{docx,pdf,excel,text}/tasks.yaml
    tools/{DOCXFileTool,PDFFileTool,ExcelFileTool,TextFileTool,UniversalFileWritingTool}.py
    pymodels/ContentExtracter.py
    pymodels/professional_style.docx
    pymodels/report.css

pyproject.toml
```

## 1. System Overview & Architecture

### Core dependencies (from `pyproject.toml`)
```
path: /pyproject.toml
```
- runtime Python >= 3.11
- agentops (observability)
- crewai (crewai[google-genai,tools]) — primary orchestration primitives (Agent, Crew, Task, Flow)
- docling — document parsing (Reader agent)
- qdrant-client — vector store client used by Reader agent tools
- langchain-text-splitters — chunking helpers
- pydantic — input/output validation
- psycopg2 — PostgreSQL access (Recruiting & Communication DB tools)
- google-api-python-client — Google Custom Search (Recruiting web search)
- pypandoc, weasyprint — file conversion for Writer agent

See `pyproject.toml` top-level dependency list for exact package names and minimum versions.

### The Manager (Orchestrator)

Manager lives at:

```
Manager/manager/src/manager/
```

Key files:
- `PlannerAgent.py` — Planner agent that decomposes the user's free-text prompt into an ordered plan (list of {agent, task}).
- `IO.py` — Pydantic input/output envelope used across Manager and Agents (`AgentInput`, `AgentOutput`, `AgentFile`).
- `flow.py` — Manager flow that executes the plan step-by-step and delegates to specific agent `Crew` or `Flow` objects.
- `crews.py` — imports and constructs agent crew classes from the `Agents/` tree, exposing them to `flow.py`.

PlannerAgent (file):

```
Manager/manager/src/manager/PlannerAgent.py
```

- Purpose: Given a user prompt, return an ordered JSON list of steps. Each step is a dictionary with keys `agent` and `task`.
- Implementation: Builds an LLM-backed `Task` using Crewai `LLM` and `Crew` to generate the plan. The output is validated with a `PlannerOutput` Pydantic model.

Manager flow (file):

```
Manager/manager/src/manager/flow.py
```

Step-by-step execution path (detailed):
1. initialize(start) — Called with `AgentInput` payload. It starts an `agentops` trace and augments the planner prompt with attached file descriptions (if any).
2. Calls `PlannerAgent.PlannerTask(planner_prompt)` to receive `self.state.plan` — a list of steps like [{"agent": "reader", "task": "..."}, ...].
3. `control_struct` router chooses whether `exceute_crew` should run (if more steps exist) or `Complete`.
4. `crew_exceution`:
   - Pulls current `step` (agent name & subquery).
   - Uses `crews.py` mapping to resolve `selected_crew` from `crew_collection`:
     - `communication` → `Communicationagent()` (Crew)
     - `reader` → `Readeragent()` (Crew)
     - `hiring` → `Recruitingagent()` (Crew)
     - `writer` → `FileGenerationFlow()` (Flow)
   - Builds `curr_input` string combining `OBJECTIVE`, `CONTEXT` (previous outputs), and a file manifest when files were provided to Manager.
   - Delegates execution:
     - If `selected_crew` is a `Crew`: `await selected_crew.crew().akickoff(input={'content': curr_input})`
     - If `selected_crew` is a `Flow`: `await selected_crew.akickoff(input={'data': curr_input})`
   - Captures textual `result`, attaches it to the trace, and appends to `exceution_history`.
   - Increments `current_step_idx` and returns to router.
5. On `Complete` the flow ends the `agentops` trace and returns an `AgentOutput` with final content and metadata about executed steps.

Notes on orchestration behavior:
- Manager treats individual Agent packages as black-box `Crew` or `Flow` modules and passes context as a stringified content payload. Agents are expected to parse and respect this input format.
- Errors captured during a crew execution will end the agentops trace with `TraceState.ERROR` and raise the exception.

## 2. Agent Documentation (Deep Dive)

For each agent package we describe: configuration mapping, crew assembly, entrypoints, and knowledge files.

---

### Communication Agent

Primary files:

```
Agents/communicationagent/src/communicationagent/crew.py
Agents/communicationagent/src/communicationagent/main.py
Agents/communicationagent/src/communicationagent/config/agents.yaml
Agents/communicationagent/src/communicationagent/config/tasks.yaml
Agents/communicationagent/src/communicationagent/tools/*.py
Agents/communicationagent/src/communicationagent/pyModels/extracter.py
```

Configuration Logic:
- Roles are defined in `config/agents.yaml`. Important agent names used by the crew:
  - `info_extracter` — extracts target recipients, message type and tone.
  - `contact_info` — queries DB to map names/group flags to contact rows.
  - `content_gen` — drafts the message body respecting tone and recipient grouping.
  - `content_verifi` — a human-in-the-loop verification step (can call review tool).
  - `send_output` — final dispatch agent (iterates recipients and calls send tools).
- Tasks are defined in `config/tasks.yaml` and map to those agents via the `agent:` field. Example: `extracting` task uses `info_extracter` and returns structured extraction.

Flow & Execution:
- `crew.py` assembles Agent objects via Crewai `@agent` methods and constructs `Task` objects with `@task` methods. Example flow inside `Communicationagent.crew()` is sequential:
  1. `extracting_task` → returns `InfoExtracter` pydantic output from `pyModels.extracter.InfoExtracter`.
  2. `contact_info_task` → uses `tools.dbSearch.dbSearchTool` to retrieve recipient addresses; depends on extracting_task.
 3. `content_gen_task` → composes message; depends on extracting and contact info.
 4. `content_verifi_task` → optionally performs human review; can set `human_input=True` in the Task config.
 5. `sending_output` → uses `emailTool` and `whatsappTool` to send messages.

Entrypoint:
- `main.py` provides a commented example runner which constructs `Communicationagent().crew().kickoff(inputs=...)`.

Knowledge Base:
- `Agents/communicationagent/knowledge/user_preference.txt` (when present) can be read by agent tools to inject user-specific defaults (tone, default sender email). The crew and tools do not automatically load this file—it's available for tool implementations or custom LLM prompts if integrated.

---

### Reader Agent

Primary files:

```
Agents/readeragent/src/readeragent/crew.py
Agents/readeragent/src/readeragent/main.py
Agents/readeragent/src/readeragent/tools/UniversalParserTool.py
Agents/readeragent/src/readeragent/tools/QuesAnswTool.py
Agents/readeragent/src/readeragent/tools/ListFilesTool.py
Agents/readeragent/src/readeragent/pymodels/descriptionModel.py
Agents/readeragent/src/readeragent/config/agents.yaml
Agents/readeragent/src/readeragent/config/tasks.yaml
```

Configuration Logic:
- `agents.yaml` defines three agent roles: `knowledge_manager`, `search_planner`, and `data_analyst`.
- `tasks.yaml` maps tasks:
  - `ingestion_task` (parsing input) to `knowledge_manager` — expects filenames.
  - `search_planning_task` to `search_planner` — depends on ingestion output.
  - `qa_task` to `data_analyst` — depends on search plan and performs Q/A against vector DB.

Flow & Execution:
- `crew.py` instantiates three Agents with tools injection:
  - `knowledge_manager`: receives `UniversalParserTool` for parsing PDFs/images into markdown and storing chunks in Qdrant.
  - `search_planner`: receives `ListFilesTool` to enumerate files and plan which files to search.
  - `data_analyst`: receives `QuesAnswTool` to query Qdrant and assemble an answer.
- `main.py` shows a small interactive runner that prompts for a query and sample filenames; it calls `Readeragent().crew().kickoff(inputs=...)`.

Knowledge Base:
- `Agents/readeragent/knowledge/user_preference.txt` (if present) is accessible to LLM prompts and tools for user-specific parsing behavior. Tools can read `LOCAL_FILES_DIR` for documents to ingest.

Reader tool implementation highlights:
- `UniversalParserTool` (see Tools API below) uses `docling` to OCR and convert PDFs/images to Markdown then chunk into documents via `MarkdownHeaderTextSplitter` and `RecursiveCharacterTextSplitter` before inserting them into Qdrant collection. It writes per-document Markdown files to `LOCAL_FILES_DIR`.
- `QuesAnswTool` executes semantic queries against Qdrant using `client.query(collection_name=..., query_text=..., limit=50)`, filters and deduplicates results, and returns a JSON or textual context payload used by the `data_analyst` agent.

---

### Recruiting Agent

Primary files:

```
Agents/recruitingagent/src/recruitingagent/crew.py
Agents/recruitingagent/src/recruitingagent/main.py
Agents/recruitingagent/src/recruitingagent/pymodels/recuirementExtracter.py
Agents/recruitingagent/src/recruitingagent/pymodels/webSearchOutput.py
Agents/recruitingagent/src/recruitingagent/tools/DBSaverTool.py
Agents/recruitingagent/src/recruitingagent/tools/searchTools/DBsearchTool.py
Agents/recruitingagent/src/recruitingagent/tools/searchTools/WebsearchTool.py
Agents/recruitingagent/src/recruitingagent/config/agents.yaml
Agents/recruitingagent/src/recruitingagent/config/tasks.yaml
```

Configuration Logic:
- Agents defined in `agents.yaml` correspond to the roles described in the design doc: `RecurimentExtracter`, `DBcandidateSearch`, `CandidateFinder`, `CandidateSaver`.
- Tasks in `tasks.yaml` map to those agents and define expected outputs, e.g., `RecurimentExtracter_task` returns a `RecuirementExtracter` Pydantic model.

Flow & Execution:
- `crew.py` assembles the recruiting crew:
  1. `RecurimentExtracter_task` — parse job description into structured `skills`, `experience`, `domain`, `budget`, `location`.
  2. `DBcandidate_search_task` — calls `DBsearchTool` with a `skill_query` list. The task registers a `callback=checkDBRes` which may short-circuit further tasks if results are found.
  3. `candidate_finding_task` — has `conditional=search_web` and only executes a web search if `DBcandidate_search_task` indicates insufficient matches (threshold logic implemented via `checkDBRes` / `search_web`). It returns a `CandidateList` Pydantic model.
  4. `candidate_saving_task` — consolidates candidates and calls `CandidateSaverTool` to persist them.

Knowledge Base:
- `Agents/recruitingagent/knowledge/user_preference.txt` can provide recruiter preferences (defaults) used by the `RecuirementExtracter` LLM prompts.

Database interactions:
- `DBsearchTool` expects PostgreSQL credentials via environment variables (`DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`). It runs SQL queries against `candidate` table using the Postgres array overlap operator `skills && %s`.
- `CandidateSaverTool` inserts rows into `candidate (name, profile_link, skills, bio, platform)` and expects input as a JSON list or similar. It uses `psycopg2` with connection params taken from environment variables.

---

### Writer Agent (File Generation)

Primary files:

```
Agents/writeragent/src/writeragent/flow.py
Agents/writeragent/src/writeragent/main.py
Agents/writeragent/src/writeragent/crews.py
Agents/writeragent/src/writeragent/config/{docx,pdf,excel,text}/agents.yaml
Agents/writeragent/src/writeragent/config/{docx,pdf,excel,text}/tasks.yaml
Agents/writeragent/src/writeragent/tools/{DOCXFileTool,PDFFileTool,ExcelFileTool,TextFileTool,UniversalFileWritingTool}.py
Agents/writeragent/src/writeragent/pymodels/ContentExtracter.py
Agents/writeragent/src/writeragent/pymodels/professional_style.docx
Agents/writeragent/src/writeragent/pymodels/report.css
```

Configuration Logic:
- Each format (docx, pdf, excel, text) has its own `agents.yaml` defining a format specialist role and `tasks.yaml` describing precise tool invocation rules (for example, `docx_task` mandates calling `Docx File Writing Tool` and returning tool confirmation).

Flow & Execution (how `flow.py` routes and dispatches):
- `FileGenerationFlow.route_request` builds a classifier Agent that analyzes `self.state['data']` and returns a classification tag: `docx_job`, `pdf_job`, `excel_job`, `markdown_job`, `text_job`.
- `execute_specialist` branches on the tag and dispatches execution to the corresponding Crew/Flow:
  - `ExcelCrew` → `ExcelCrew().crew().kickoff(inputs={"data": user_input})`
  - `DocxCrew` → `DocxCrew().crew().kickoff(inputs={"data": user_input})`
  - `TextCrew` → `TextCrew().crew().kickoff(inputs={"data": user_input})`
  - `PdfCrew` → `PdfCrew().crew().kickoff(inputs={"data": user_input})`

Special handling — writer agent formats & assets:
- `Agents/writeragent/src/writeragent/config/` contains per-format subfolders: `docx`, `pdf`, `excel`, and `text` each with `agents.yaml` and `tasks.yaml`. These YAML files precisely map the agent name to the task the agent must perform and mandate which tool must be called (examples: `Docx File Writing Tool` for `.docx`).
- The Writer tools are implemented to convert Markdown content into target formats using `pypandoc` and `weasyprint`:
  - `DOCXFileWritingTool` uses `pypandoc.convert_file(..., to='docx', extra_args=['--reference-doc=...'])` and expects a `--reference-doc` (Word style template) at `STYLE_PATH_DOCX` environment variable. The repository includes `Agents/writeragent/src/writeragent/pymodels/professional_style.docx` as a style asset.
  - `PDFFileWritingTool` converts markdown to HTML with `markdown` and then renders PDF with `weasyprint` using `report.css` at `Agents/writeragent/src/writeragent/pymodels/report.css` (referenced by `CSS_PATH` env var).
  - `ExcelFileWritingTool` accepts a CSV string (or `.csv`) and writes `.xlsx` using `pandas`.
  - `TextFileWritingTool` writes `.txt` or `.md` files directly.
  - `UniversalFileWritingTool` dispatches among these implementations when called by a higher-level flow.

Writer environment variables used at runtime (examples):
```
WRITTEN_PATH=/path/to/output
STYLE_PATH_DOCX=/path/to/professional_style.docx
CSS_PATH=/path/to/report.css
```

## 3. Special Handling Instructions

### Writer Agent Complexity — detailed mapping

- Per-format config directories exist under:
```
Agents/writeragent/src/writeragent/config/docx/
Agents/writeragent/src/writeragent/config/pdf/
Agents/writeragent/src/writeragent/config/excel/
Agents/writeragent/src/writeragent/config/text/
```
- Each `agents.yaml` describes the role/backstory for a specialist (e.g., `pdf_specialist`, `docx_specialist`, `excel_specialist`, `text_specialist`).
- Each `tasks.yaml` contains a task that references the `agent` name and mandates the exact tool call (for example `docx_task` requires calling `Docx File Writing Tool` and returning its confirmation message).
- `flow.py` (`FileGenerationFlow`) classifies the user request and routes to the correct specialist crew; that crew's tasks then transform the input into the required formatted markdown/CSV and call the mandated writing tool.

Style assets:
- `Agents/writeragent/src/writeragent/pymodels/professional_style.docx` — used as `--reference-doc` for `pypandoc` when producing DOCX files.
- `Agents/writeragent/src/writeragent/pymodels/report.css` — used by `weasyprint` as the stylesheet for PDF rendering. It contains table rules, headers, pagination rules, and font fallback settings.

### Database Integration (Recruiting & Communication)

- PostgreSQL is the canonical relational store used for candidate storage and communication contact lookup.
- Recruiting tools use environment variables for DB configuration:
  - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`.
- `DBsearchTool` SQL behavior:
  - Query: `SELECT name, bio, profile_link FROM candidate WHERE skills && %s;` — uses Postgres array operator `&&` to find candidates whose `skills` array overlaps with the provided skill list.
  - Returns rows with `name`, `profile_link`, `bio` formatted into a newline-separated string.
- `CandidateSaverTool` behavior:
  - Accepts `candidateList` argument (JSON string, list, or dict wrapper), normalizes `skills` to a list and inserts rows into `candidate` table with columns `(name, profile_link, skills, bio, platform)`. Uses `RETURNING id` semantics to detect success.
  - Important: `CandidateSaverTool` performs per-candidate inserts inside a loop and commits at the end. It executes rollback on exceptions.

### Qdrant / Vector DB (Reader agent)

- `UniversalParserTool` creates and populates the Qdrant collection at runtime when needed:
  - Reads `QDRANT_PATH` and `COLLECTION_NAME` from environment variables.
  - Uses `client.create_collection(collection_name=..., vectors_config=client.get_fastembed_vector_params())` when the collection does not exist.
  - Inserts documents as `client.add(collection_name=..., documents=text, metadata=metadata, ids=[uuid4...])` where `metadata` is a list of dicts with keys: `source` (basename of filename) and `chunk_id` (integer chunk index).
  - The stored `document` values are the chunk text content.
- `QuesAnswTool` queries with `client.query(collection_name=..., query_text=query, limit=50)` and post-filters (filename filter, dedupe by content prefix, limit 10). It returns combined context strings per target.

## 4. Tools API (file-level catalog)

Each tool implements a Crewai `BaseTool` subclass. The list below maps the tool class to the function, schema, inputs and outputs as implemented in code.

- `UniversalParserTool` (class name: `UniversalParserTool`)
  - File: `Agents/readeragent/src/readeragent/tools/UniversalParserTool.py`
  - Purpose: Parse PDFs/images -> Markdown, chunk text, store chunks in Qdrant.
  - Input schema: `UniversalParserInput` { `filenames: List[str]` }
  - Returns: A textual report string listing success/failure per file (e.g., "Successfully stored N chunks from file").
  - Side effects: writes markdown files to `LOCAL_FILES_DIR` and inserts records into Qdrant collection with metadata `{source, chunk_id}`.

- `QuesAnswTool` (class name: `QuesAnswTool`)
  - File: `Agents/readeragent/src/readeragent/tools/QuesAnswTool.py`
  - Purpose: Execute semantic search queries against Qdrant and return assembled contexts.
  - Input schema: `QuesAnswInput` { `targets: List[SearchTarget]` }, where `SearchTarget` is `{query: str, filter_filename: Optional[str]}`.
  - Returns: JSON string containing array of contexts: [{Source, Content}, ...] or an error string.

- `ListFilesTool` (class name: `ListFilesTool`)
  - File: `Agents/readeragent/src/readeragent/tools/ListFilesTool.py`
  - Purpose: List files in `LOCAL_FILES_DIR` for the planner/agents.
  - Input schema: empty base model
  - Returns: Multi-line string "Available Files:\nfile1\nfile2..." or an error message.

- `SendEmailTool` (class name: `SendEmailTool`) — exported name `SendEmailTool` in code
  - File: `Agents/communicationagent/src/communicationagent/tools/emailTool.py`
  - Purpose: Send email via SMTP (Gmail example) and attach files.
  - Input schema: `EmailInput` { recipient: str, subject: str, body: str, files: List[str] }
  - Returns: `str` confirmation or failure message. Uses environment variables `COMMUNICATION_EMAIL` and `APP_PASSWORD`.

- `SendWhatsAppTool` (class name: `SendWhatsAppTool`)
  - File: `Agents/communicationagent/src/communicationagent/tools/whatsappTool.py`
  - Purpose: Send WhatsApp message via Twilio API.
  - Input schema: `WhatsAppInput` { phone: str, message: str }
  - Returns: `str` success message with SID or an error string. Uses `TWILIO_SID` and `TWILIO_AUTH_TOKEN` env vars.

- `dbSearchTool` (class name: `dbSearchTool`)
  - File: `Agents/communicationagent/src/communicationagent/tools/dbSearch.py`
  - Purpose: Query local PostgreSQL for contact email/phone given a name or group flag.
  - Input schema: `dbSearchInput` { name: str, typeof: str }
  - Returns: newline-separated list of `Name: ... | Email: ... | Phone: ...` strings.
  - NOTE: connection parameters are currently hard-coded in the tool (host=localhost, dbname=kins, user=postgres, password=post00, port=5432) — adjust as required.

- `CandidateSaverTool` (class name: `CandidateSaverTool`)
  - File: `Agents/recruitingagent/src/recruitingagent/tools/DBSaverTool.py`
  - Purpose: Persist candidate list(s) to PostgreSQL `candidate` table. Normalizes `skills` to a list.
  - Input schema: `DBSaverToolInput` { candidateList: Union[str,List[Dict],Dict] }
  - Returns: String summary: "Successfully saved X and Skiped Y candidates to the database." or error string.
  - Connection: uses env-based `DB_PARAMS` (DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT).

- `DBsearchTool` (class name: `DBsearchTool`)
  - File: `Agents/recruitingagent/src/recruitingagent/tools/searchTools/DBsearchTool.py`
  - Purpose: Search `candidate` table for matching skills.
  - Input schema: `DBsearchToolInput` { skill_query: List[str] }
  - Returns: newline-separated candidate summaries `Name: ... | Profile Link: ... | Bio: ...`.

- `WebSearchTool` (class name: `WebSearchTool`) — wrapper for external web search
  - File: `Agents/recruitingagent/src/recruitingagent/tools/searchTools/WebsearchTool.py`
  - Purpose: Use Google Custom Search (or other web APIs) to find LinkedIn profiles and return structured candidate metadata. (Implementation exists as a wrapper in `WebSearchTool.py`.)

- Writer tools:
  - `DOCXFileWritingTool` (`DOCXFileWritingTool`) — `Agents/writeragent/src/writeragent/tools/DOCXFileTool.py`
    - Input: `{content: str, filename: str}`. Writes DOCX using `pypandoc` and `STYLE_PATH_DOCX`.
  - `PDFFileWritingTool` (`PDFFileWritingTool`) — `Agents/writeragent/src/writeragent/tools/PDFFileTool.py`
    - Input: `{content: str, filename: str}`. Converts Markdown -> HTML -> PDF using `markdown` + `weasyprint` and `CSS_PATH`.
  - `ExcelFileWritingTool` (`ExcelFileWritingTool`) — `Agents/writeragent/src/writeragent/tools/ExcelFileTool.py`
    - Input: `{content: str, filename: str}`. Accepts CSV or writes `.xlsx` via `pandas`.
  - `TextFileWritingTool` (`TextFileWritingTool`) — `Agents/writeragent/src/writeragent/tools/TextFileTool.py`
    - Input: `{content: str, filename: str}`. Writes `.txt` or `.md`.
  - `UniversalFileWritingTool` (`UniversalFileWritingTool`) — `Agents/writeragent/src/writeragent/tools/UniversalFileWritingTool.py`
    - Input: `{content: str, filename: str}`. Routes creation to the appropriate format helper (text, excel, pdf, docx).

## 5. Data Models (Pydantic / Schemas)

This project uses small Pydantic models to enforce structured task outputs.

- `Manager/manager/src/manager/IO.py`:
  - `AgentFile` { `path: str`, `description: Optional[str]` }
  - `AgentInput` { `user_id: str`, `session_id: str`, `task_id: str`, `content: str`, `files: List[AgentFile]`, `context: Dict[str, Any]` }
  - `AgentOutput` { `status: str`, `content: str`, `generated_files: List[str]`, `metadata: Dict[str, Any]` }

- `Reader`:
  - `Agents/readeragent/src/readeragent/pymodels/descriptionModel.py` → `DescriptionExtracter` { `description: str`, `filename: str` }

- `Recruiting`:
  - `Agents/recruitingagent/src/recruitingagent/pymodels/recuirementExtracter.py` → `RecuirementExtracter` with fields:
    - `skills: List[str]`, `experience: str`, `domain: str`, `budget: str`, `location: str`, `gender: str`, `age: str`.
  - `Agents/recruitingagent/src/recruitingagent/pymodels/webSearchOutput.py` → `Candidate` and `CandidateList`:
    - `Candidate`: `name: str`, `profile_link: str`, `bio: str`, `skills: List[str]`, `match_score: int`.
    - `CandidateList`: `candidateList: List[Candidate]`.

- `Writer`:
  - `Agents/writeragent/src/writeragent/pymodels/ContentExtracter.py` → `ContentExtracter` { `content: str`, `filename: str` }

- `Communication`:
  - `Agents/communicationagent/src/communicationagent/pyModels/extracter.py` — referenced in `crew.py` as `InfoExtracter` (used as `output_pydantic` in extracting task). (Open the file for exact fields if necessary.

## Usage & Runtime Notes

- Environment: Use a `.env` at repo root with the environment variables referred to in this document (OPENAI_MODEL_NAME, OPENAI_API_BASE, QDRANT_PATH, COLLECTION_NAME, LOCAL_FILES_DIR, DB_HOST/DB_NAME/DB_USER/DB_PASSWORD/DB_PORT, TWILIO_SID/TWILIO_AUTH_TOKEN, COMMUNICATION_EMAIL/APP_PASSWORD, WRITTEN_PATH, CSS_PATH, STYLE_PATH_DOCX, AGENT_OPS_API_KEY).
- Run agents individually via their `main.py` examples, or invoke `Manager` flow (the Manager's `main.py` is present but empty — the `flow` class is the important orchestrator for programmatic integration).

## Troubleshooting and Operational Guidance

- Qdrant: ensure `QDRANT_PATH` is set and readable by the process. The Reader's parser will create the collection if missing.
- PostgreSQL: ensure tables exist (e.g., `candidate` table with `skills` as text[]). Example schema suggested in project design doc (RecruitingAgent.md):
```
CREATE TABLE candidate (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255),
  bio TEXT,
  profile_link VARCHAR(255),
  skills TEXT[]
);
```
- Writer: install `pypandoc` + `pandoc` system binary or ensure `pypandoc` has a working backend; `weasyprint` requires additional system libraries for rendering.

## Next Steps / Recommended Improvements

- Centralize DB credentials: several tools use different connection strategies (some hard-coded local credentials, others use env vars). Consolidate to `DB_PARAMS` via env.
- Add unit tests for each `BaseTool` to validate external integrations in isolation (mock Qdrant client, psycopg2, Twilio).
- Add a Manager `main.py` that accepts HTTP or RPC payloads to run the `Manager` flow as a service.

---

This file is intended as a single-source technical reference for new engineers joining the project. For implementation-level details, inspect the file paths listed in the `Project Structure` section.

Last updated: 2026-02-07
