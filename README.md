# Kins Agents Suite

An ensemble of small, composable multi-agent utilities for document ingestion, content extraction, communication, and recruiting workflows. The repository contains focused agent packages (Reader, Writer, Recruiting, Communication) built with CrewAI-style orchestration patterns and small, testable tool modules for IO and integrations.

## Overview

Kins Agents Suite is a set of lightweight agent packages designed to automate document parsing, semantic search, content extraction and candidate sourcing in reproducible, modular pipelines. Each agent package is implemented as a small Python package under `src/` with YAML-configured agent and task definitions, and a concise set of tools and pydantic-style models for inputs/outputs.

Key capabilities:
- Ingest and parse multi-format documents (PDF, images, DOCX, Excel, plain text) with chunking and metadata preservation
- Perform semantic vector search using a Qdrant-backed workflow
- Extract and normalize structured information from natural-job descriptions (recruiting)
- Programmatically read and write DOCX/PDF/Excel/text files and pipeline transformations (writer)
- Send and review messages across channels (email, WhatsApp), and search a local DB for knowledge lookups (communication)

## Project Structure

```
Kins/                         # repository root
├── README.md                  # (this file)
├── pyproject.toml             # Project configuration (may contain top-level deps)
├── TEMPLATE.md                # README skeleton used for this file
├── communicationagent.md      # Communication agent design doc
├── ReaderAgent.md             # Reader agent design doc
├── WriterAgent.md             # Writer agent design doc
├── RecruitingAgent.md         # Recruiting agent design doc
├── Agents/                    # Agent package folders
│   ├── communicationagent/
│   │   ├── src/communicationagent/...
│   ├── readeragent/
│   │   ├── src/readeragent/...
│   ├── recruitingagent/
│   │   ├── src/recruitingagent/...
│   └── writeragent/
│       ├── src/writeragent/...
└── docs/ etc.
```

## Architecture

### System Design

Kins uses a multi-package, multi-agent design where each agent package exposes:
- an entry point (`src/<agent>/main.py`) to bootstrap example runs
- a crew/agent definition module (`crew.py`) and YAML configuration in `src/<agent>/config/agents.yaml` and `tasks.yaml`
- a small set of tools under `src/<agent>/tools/` for integrations (DB, web search, file IO)
- lightweight models under `src/<agent>/pymodels/` to validate or format structured outputs

Agents communicate via payloads and return structured outputs; conditional branching and sequential orchestration are encoded in task YAML and crew logic.

### Communication Protocol (how `communicationagent.md` maps to code)

- High level spec: `communicationagent.md` describes channel tools (email, WhatsApp), a DB search tool and a review tool. The implementation lives at:
  - Entry: [src/communicationagent/main.py](src/communicationagent/main.py)
  - Crew: [src/communicationagent/crew.py](src/communicationagent/crew.py)
  - Tools: [src/communicationagent/tools/emailTool.py](src/communicationagent/tools/emailTool.py), [src/communicationagent/tools/whatsappTool.py](src/communicationagent/tools/whatsappTool.py), [src/communicationagent/tools/dbSearch.py](src/communicationagent/tools/dbSearch.py), [src/communicationagent/tools/reviewTool.py](src/communicationagent/tools/reviewTool.py)

The tools implement simple send/format/search/review functions and are invoked by agent tasks defined in the YAML files under `src/communicationagent/config/`.

The communication pattern is local, synchronous function calls between crew/task orchestration and tool modules; external integrations (SMTP, WhatsApp API) are abstracted behind tool interfaces.

## Installation

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies. This project collects agent packages that expect common tooling (CrewAI-style orchestration, Pydantic, vector DB client). Recommended packages (not an exhaustive list - see `pyproject.toml`):

```bash
pip install crewai[tools] docling qdrant-client langchain pydantic python-dotenv agentops psycopg2 google-api-python-client
```

Or install editable package(s) if each agent has a local `pyproject.toml`:

```bash
pip install -e .
```

3. Environment variables - create `.env` in repository root with the following (examples from the design docs):

```env
# LLM / API
OPENAI_MODEL_NAME=your-model-name
OPENAI_API_BASE=http://localhost:8000/v1

# Qdrant (Reader Agent)
QDRANT_PATH=/path/to/qdrant/db
COLLECTION_NAME=your_collection_name

# Local files directory (Reader Agent)
LOCAL_FILES_DIR=/path/to/local/files

# PostgreSQL (Recruiting Agent)
DB_HOST=localhost
DB_NAME=recruiting_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432

# Google Custom Search (Recruiting Agent)
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_custom_search_engine_id
```

Notes:
- The Reader Agent expects a Qdrant instance (or local qdrant path) and optionally Docling/OCR dependencies for PDF/image parsing.
- The Recruiting Agent expects PostgreSQL credentials if using DB search and saver tools.

## Usage

Each agent package includes a small runner in `src/<agent>/main.py`. Typical usage:

Run the Reader agent (ingest + query example):

```bash
python src/readeragent/main.py
```

Run the Recruiting agent (CLI prompt expects a job description):

```bash
python src/recruitingagent/main.py
```

Run the Writer agent example runner:

```bash
python src/writeragent/main.py
```

Run the Communication agent example runner:

```bash
python src/communicationagent/main.py
```

Each runner typically prompts or reads sample inputs; see the package README and `src/<agent>/config/` YAML files for task-specific input formats.

## Agent Breakdown

**Reader Agent** (see [ReaderAgent.md](ReaderAgent.md) and implementation at `src/readeragent`)

- Purpose: Document ingestion, chunking, semantic indexing and question-answering
- Entry point: [src/readeragent/main.py](src/readeragent/main.py)
- Crew: [src/readeragent/crew.py](src/readeragent/crew.py)
- Config: [src/readeragent/config/agents.yaml](src/readeragent/config/agents.yaml) and [src/readeragent/config/tasks.yaml](src/readeragent/config/tasks.yaml)
- Tools:
  - [src/readeragent/tools/UniversalParserTool.py](src/readeragent/tools/UniversalParserTool.py): Parses PDFs/images (OCR), chunking and metadata
  - [src/readeragent/tools/ListFilesTool.py](src/readeragent/tools/ListFilesTool.py): Discovers files in `LOCAL_FILES_DIR`
  - [src/readeragent/tools/QuesAnswTool.py](src/readeragent/tools/QuesAnswTool.py): Executes vector search in Qdrant and assembles top results
- Models: [src/readeragent/pymodels/descriptionModel.py](src/readeragent/pymodels/descriptionModel.py)

- Workflow (explicit triggers, inputs, outputs, tools):
  1. Ingestion Task (trigger: user or scheduled run)
     - Input: list of filenames or folder path
     - Tool: `UniversalParserTool` (PDF/image parsing, chunking)
     - Output: chunks saved to Qdrant collection with metadata `source_filename`
  2. Search Planning Task (trigger: user question)
     - Input: natural language query
     - Tool: `ListFilesTool` to enumerate candidates, planner logic in `crew.py`
     - Output: a Search Manifest mapping query components to filenames
  3. QA Task (trigger: search manifest produced)
     - Input: Search Manifest
     - Tool: `QuesAnswTool` performing top-k semantic retrieval from Qdrant
     - Output: Synthesized answer with citations (source filenames)

**Recruiting Agent** (see [RecruitingAgent.md](RecruitingAgent.md) and implementation at `src/recruitingagent`)

- Purpose: Extract structured requirements from job descriptions, search internal DB and external web (LinkedIn), and persist candidate records
- Entry point: [src/recruitingagent/main.py](src/recruitingagent/main.py)
- Crew: [src/recruitingagent/crew.py](src/recruitingagent/crew.py)
- Config: [src/recruitingagent/config/agents.yaml](src/recruitingagent/config/agents.yaml) and [src/recruitingagent/config/tasks.yaml](src/recruitingagent/config/tasks.yaml)
- Tools:
  - [src/recruitingagent/tools/DBSaverTool.py](src/recruitingagent/tools/DBSaverTool.py): Writes candidates to PostgreSQL
  - [src/recruitingagent/tools/searchTools/DBsearchTool.py](src/recruitingagent/tools/searchTools/DBsearchTool.py): Internal DB search
  - [src/recruitingagent/tools/searchTools/WebsearchTool.py](src/recruitingagent/tools/searchTools/WebsearchTool.py): Google Custom Search wrapper for LinkedIn queries
- Models: [src/recruitingagent/pymodels/recuirementExtracter.py](src/recruitingagent/pymodels/recuirementExtracter.py), [src/recruitingagent/pymodels/webSearchOutput.py](src/recruitingagent/pymodels/webSearchOutput.py)

- Workflow (explicit triggers, inputs, outputs, tools):
  1. `RecuirementExtracter` (trigger: job description input)
     - Input: raw job description text
     - Tool/Model: `recuirementExtracter.py` Pydantic schema
     - Output: JSON with keys `skills`, `experience`, `domain`, `budget`, `location`, `gender`, `age`
  2. `DBcandidateSearch` (trigger: requirements produced)
     - Input: structured requirements
     - Tool: `DBsearchTool` queries internal PostgreSQL
     - Expected Output: at least 5 candidates; if fewer, output `THRESHOLD_NOT_MET`
  3. `CandidateFinder` (trigger: `THRESHOLD_NOT_MET` from DB search)
     - Input: requirements
     - Tool: `WebsearchTool` (Google CSE, filters `site:linkedin.com/in`)
     - Output: up to 10 external candidate objects with `name`, `profile_link`, `bio`, `skills`, `match_score`
  4. `CandidateSaver` (trigger: consolidated candidate list)
     - Input: consolidated candidates from DB and web
     - Tool: `DBSaverTool` (transaction-safe insert, dedupe)
     - Output: persisted database status / IDs

**Writer Agent** (see [WriterAgent.md](WriterAgent.md) and implementation at `src/writeragent`)

- Purpose: Extract content from multiple file formats and provide writing and export pipelines
- Entry point: [src/writeragent/main.py](src/writeragent/main.py)
- Crew: [src/writeragent/crews.py](src/writeragent/crews.py) and orchestration in [src/writeragent/flow.py](src/writeragent/flow.py)
- Tools (file IO):
  - [src/writeragent/tools/DOCXFileTool.py](src/writeragent/tools/DOCXFileTool.py)
  - [src/writeragent/tools/PDFFileTool.py](src/writeragent/tools/PDFFileTool.py)
  - [src/writeragent/tools/ExcelFileTool.py](src/writeragent/tools/ExcelFileTool.py)
  - [src/writeragent/tools/TextFileTool.py](src/writeragent/tools/TextFileTool.py)
  - [src/writeragent/tools/UniversalFileWritingTool.py](src/writeragent/tools/UniversalFileWritingTool.py)
- Models: [src/writeragent/pymodels/ContentExtracter.py](src/writeragent/pymodels/ContentExtracter.py)

- Workflow (explicit triggers, inputs, outputs, tools):
  - File Extraction Task (trigger: file input or folder)
    - Input: file path
    - Tool: format-specific tool (DOCX/PDF/Excel/Text)
    - Output: extracted text/content segments
  - Content Processing Task
    - Input: extracted content
    - Tool: `ContentExtracter` model + `flow.py` logic
    - Output: normalized content suitable for writing/export (DOCX, PDF, Markdown, Excel)

**Communication Agent** (see [communicationagent.md](communicationagent.md) and implementation at `Agents/communicationagent`)

- Purpose: Format and send messages, run local DB/knowledge searches, and review message content
- Entry point: [Agents/communicationagent/src/communicationagent/main.py](Agents/communicationagent/src/communicationagent/main.py)
- Tools: [Agents/communicationagent/src/communicationagent/tools/emailTool.py](Agents/communicationagent/src/communicationagent/tools/emailTool.py), [Agents/communicationagent/src/communicationagent/tools/whatsappTool.py](Agents/communicationagent/src/communicationagent/tools/whatsappTool.py), [Agents/communicationagent/src/communicationagent/tools/dbSearch.py](Agents/communicationagent/src/communicationagent/tools/dbSearch.py), [Agents/communicationagent/src/communicationagent/tools/reviewTool.py](Agents/communicationagent/src/communicationagent/tools/reviewTool.py)

- Workflow summary:
  - Compose/Format message (trigger: user prompt or task input)
    - Tools: `emailTool`, `whatsappTool`
    - Outputs: formatted message payloads (recipient/address, subject, body, metadata)
  - DB Search (trigger: knowledge lookup requested)
    - Tool: `dbSearch.py`
    - Output: matching knowledge snippets
  - Review (trigger: message ready to send)
    - Tool: `reviewTool.py`
    - Output: review score or suggested edits

## Architecture Mapping: How docs translate to code

- The design documents (`ReaderAgent.md`, `WriterAgent.md`, `RecruitingAgent.md`, `communicationagent.md`) describe agent responsibilities, triggers, and expected outputs. Each agent package in the repository maps the described responsibilities to:
  - YAML configuration for agent/backstory and tasks: `src/<agent>/config/agents.yaml` and `tasks.yaml`
  - Task orchestration and choice logic: `src/<agent>/crew.py` (or `crews.py`) and `main.py` which assemble the crew and call tasks in sequence
  - Concrete tool implementations: `src/<agent>/tools/*` for external/system integrations
  - Data validation / schema helpers: `src/<agent>/pymodels/*`

- Conditional flows described in the design docs (for example, `THRESHOLD_NOT_MET` trigger in the Recruiting Agent) are encoded in task logic and crew orchestration files, and enforced by the tool outputs returned to subsequent tasks.

## Dependencies

Primary dependencies described across agent docs (install as needed):
- crewai[tools] (Crew orchestration helpers)
- pydantic
- docling (document parsing / OCR)
- qdrant-client (vector store client) or qdrant local runtime
- langchain (text splitting / embedding helpers)
- python-dotenv
- psycopg2 (PostgreSQL)
- google-api-python-client (Google Custom Search)
- agentops (observability - optional)

Check `pyproject.toml` at repository root or per-agent `pyproject.toml` files for exact pinned versions.

## Development Notes

- Add or update `.env` values before running agents that require external services (see Installation > Environment variables).
- Use the `src/<agent>/config/` YAML files to tune agents' behavior, backstories, and task pipelines.
- The code is intentionally modular: add new tools under `src/<agent>/tools` and wire them into tasks via crew/task YAML.

## Troubleshooting

- If Qdrant queries return no results: verify ingestion completed and `COLLECTION_NAME` matches.
- If DB search or saver fails: verify PostgreSQL connection environment variables and that target tables exist.
- If Google web searches fail: verify `GOOGLE_API_KEY` and `GOOGLE_CSE_ID`.

## Examples

- Run a quick recruiting example:

```bash
python src/recruitingagent/main.py
# Follow prompt to paste a job description
```

- Run a Reader ingestion and query example:

```bash
python src/readeragent/main.py
# Provide filenames or a folder path and a natural language question
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new tools or agent logic under the package `tests/` directories
4. Open a pull request describing changes and runtime impacts

## License

Add a `LICENSE` file to the repository to clarify permissive or restrictive terms. No license is attached by default in this snapshot.

---

Last updated: 2026-02-07

```
Kins
├─ .env
├─ .python-version
├─ Agents
│  ├─ communicationagent
│  │  ├─ knowledge
│  │  │  └─ user_preference.txt
│  │  ├─ src
│  │  │  └─ communicationagent
│  │  │     ├─ __init__.py
│  │  │     ├─ config
│  │  │     │  ├─ agents.yaml
│  │  │     │  └─ tasks.yaml
│  │  │     ├─ crew.py
│  │  │     ├─ main.py
│  │  │     ├─ pyModels
│  │  │     │  └─ extracter.py
│  │  │     └─ tools
│  │  │        ├─ __init__.py
│  │  │        ├─ dbSearch.py
│  │  │        ├─ emailTool.py
│  │  │        ├─ reviewTool.py
│  │  │        └─ whatsappTool.py
│  │  └─ tests
│  ├─ localfiles/
│  ├─ qdrant_db
│  │  ├─ .lock
│  │  ├─ collection
│  │  │  └─ local_documents
│  │  │     └─ storage.sqlite
│  │  └─ meta.json
│  ├─ readeragent
│  │  ├─ knowledge
│  │  │  └─ user_preference.txt
│  │  ├─ src
│  │  │  └─ readeragent
│  │  │     ├─ __init__.py
│  │  │     ├─ config
│  │  │     │  ├─ agents.yaml
│  │  │     │  └─ tasks.yaml
│  │  │     ├─ crew.py
│  │  │     ├─ main.py
│  │  │     ├─ pymodels
│  │  │     │  ├─ __init__.py
│  │  │     │  └─ descriptionModel.py
│  │  │     └─ tools
│  │  │        ├─ ListFilesTool.py
│  │  │        ├─ QuesAnswTool.py
│  │  │        └─ UniversalParserTool.py
│  │  └─ tests
│  ├─ recruitingagent
│  │  ├─ knowledge
│  │  │  └─ user_preference.txt
│  │  ├─ pyproject.toml
│  │  ├─ src
│  │  │  └─ recruitingagent
│  │  │     ├─ __init__.py
│  │  │     ├─ config
│  │  │     │  ├─ agents.yaml
│  │  │     │  └─ tasks.yaml
│  │  │     ├─ crew.py
│  │  │     ├─ main.py
│  │  │     ├─ pymodels
│  │  │     │  ├─ recuirementExtracter.py
│  │  │     │  └─ webSearchOutput.py
│  │  │     └─ tools
│  │  │        ├─ DBSaverTool.py
│  │  │        ├─ __init__.py
│  │  │        └─ searchTools
│  │  │           ├─ DBsearchTool.py
│  │  │           └─ WebsearchTool.py
│  │  └─ tests
│  ├─ writeragent
│  │  ├─ knowledge
│  │  ├─ src
│  │  │  └─ writeragent
│  │  │     ├─ config
│  │  │     │  ├─ docx
│  │  │     │  │  ├─ agents.yaml
│  │  │     │  │  └─ tasks.yaml
│  │  │     │  ├─ excel
│  │  │     │  │  ├─ agents.yaml
│  │  │     │  │  └─ tasks.yaml
│  │  │     │  ├─ pdf
│  │  │     │  │  ├─ agents.yaml
│  │  │     │  │  └─ tasks.yaml
│  │  │     │  └─ text
│  │  │     │     ├─ agents.yaml
│  │  │     │     └─ tasks.yaml
│  │  │     ├─ crews.py
│  │  │     ├─ flow.py
│  │  │     ├─ main.py
│  │  │     ├─ pymodels
│  │  │     │  ├─ ContentExtracter.py
│  │  │     │  ├─ professional_style.docx
│  │  │     │  └─ report.css
│  │  │     └─ tools
│  │  │        ├─ DOCXFileTool.py
│  │  │        ├─ ExcelFileTool.py
│  │  │        ├─ PDFFileTool.py
│  │  │        ├─ TextFileTool.py
│  │  │        └─ UniversalFileWritingTool.py
│  │  └─ tests
│  └─ writtenFiles/
├─ Manager
│  └─ manager
│     ├─ src
│     │  └─ manager
│     │     ├─ IO.py
│     │     ├─ PlannerAgent.py
│     │     ├─ __init__.py
│     │     ├─ crews.py
│     │     ├─ flow.py
│     │     ├─ main.py
│     │     └─ tools
│     │        ├─ __init__.py
│     │        └─ custom_tool.py
│     └─ tests
├─ README.md
├─ ReaderAgent.md
├─ RecruitingAgent.md
├─ TEMPLATE.md
├─ WriterAgent.md
├─ communicationagent.md
├─ docs
├─ pyproject.toml
└─ uv.lock

```
