# Reader Agent

An AI-powered multi-agent system for intelligent document parsing, search planning, and question-answering across PDFs and images using CrewAI and vector databases.

## Overview

Reader Agent is a sophisticated AI system that leverages CrewAI's multi-agent framework to process and query document collections. The system breaks down complex document retrieval tasks into specialized roles: a knowledge manager for ingesting documents, a search planner for mapping queries to relevant files, and a data analyst for synthesizing answers. It combines advanced document parsing (Docling), vector embeddings (Qdrant), and LLM-powered reasoning to provide accurate, context-aware answers from document collections.

Key capabilities:
- **Multi-format document parsing** - Extract text and structure from PDFs and images using advanced OCR and document understanding
- **Vector-based semantic search** - Index documents and retrieve relevant chunks based on semantic similarity
- **Intelligent query routing** - Automatically map user questions to relevant documents and create search plans
- **Multi-agent orchestration** - Coordinate specialized agents for parsing, planning, and analysis tasks
- **Sequential task workflow** - Process documents through ingestion, planning, and QA stages in optimal order

## Project Structure

```
readeragent/
├── README.md                  # Project documentation (this file)
├── TEMPLATE.md                # README template
├── knowledge/
│   └── user_preference.txt    # User context and preferences
├── src/
│   └── readeragent/
│       ├── __init__.py
│       ├── main.py           # Entry point - runs the crew with user input
│       ├── crew.py           # CrewAI agent and task definitions
│       ├── config/
│       │   ├── agents.yaml   # Agent role definitions and behaviors
│       │   └── tasks.yaml    # Task descriptions and expected outputs
│       ├── pymodels/
│       │   ├── __init__.py
│       │   └── descriptionModel.py  # Pydantic models for data validation
│       └── tools/
│           ├── __init__.py
│           ├── UniversalParserTool.py    # Document parsing and indexing
│           ├── ListFilesTool.py         # File discovery and listing
│           └── QuesAnswTool.py          # Vector search and retrieval
└── tests/                    # Test files (to be populated)
```

## Architecture

### System Design

The Reader Agent implements a **multi-agent workflow** where different agents with specialized roles collaborate sequentially to answer user questions about document collections. Each agent receives input from previous agents and uses specialized tools to perform its role. The workflow follows a three-stage pipeline:

1. **Ingestion Stage** - Parse and index documents into the vector database
2. **Planning Stage** - Map user query to specific files and create search manifest
3. **QA Stage** - Retrieve relevant chunks and synthesize final answer

### Core Components

#### Component 1: Knowledge Manager Agent
- **Purpose**: Ingest and index unstructured files (PDFs, images) into the Qdrant vector database
- **Key Responsibilities**:
  - Parse files using advanced Docling techniques with OCR and table structure recognition
  - Chunk parsed documents into manageable segments
  - Embed and store chunks in Qdrant vector database with metadata
  - Report ingestion status and handle processing errors

#### Component 2: Search Planner Agent
- **Purpose**: Map user questions to specific files on disk
- **Key Responsibilities**:
  - List available files in the system using List Files Tool
  - Analyze user query and identify relevant information needs
  - Match query components to specific filenames
  - Generate a structured Search Manifest for the data analyst

#### Component 3: Data Analyst Agent
- **Purpose**: Execute search plan and synthesize answers from retrieved data
- **Key Responsibilities**:
  - Read and interpret the Search Manifest from the planner
  - Execute Question Answer Tool with specified file and query targets
  - Process retrieved chunks and extract relevant information
  - Compose comprehensive final answer with proper citations

### Tools

#### Universal Parser Tool
Parses documents using Docling with configuration for:
- **PDF Processing**: OCR enabled, table structure recognition, CPU acceleration
- **Image Processing**: Supports image documents
- **Chunking**: Markdown header-aware and recursive character splitting
- **Storage**: Persists chunks to Qdrant with source filename metadata

#### List Files Tool
Lists all available files in the configured local directory. Used by Search Planner to determine which documents are available for querying.

#### Question Answer Tool
Performs semantic vector search against the Qdrant database:
- Accepts list of search targets (query + optional filename filter)
- Retrieves top-50 most relevant chunks for each query
- Filters results by source filename if specified
- Deduplicates similar chunks and returns structured context

### Data Models

#### DescriptionExtracter
```python
{
    "description": str,  # Information to retrieve from document
    "filename": str      # Name of the file to process
}
```

#### SearchTarget
```python
{
    "query": str,                 # Specific question or request
    "filter_filename": Optional[str]  # Filename to search in (None = search all)
}
```

#### QuesAnswInput
```python
{
    "targets": List[SearchTarget]  # List of search queries with filenames
}
```

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# LLM Configuration
OPENAI_MODEL_NAME=your-model-name
OPENAI_API_BASE=http://your-api-base:port/v1

# Vector Database Configuration
QDRANT_PATH=/path/to/qdrant/db
COLLECTION_NAME=your_collection_name

# File Storage Configuration
LOCAL_FILES_DIR=/path/to/local/files
```

### Configuration Files

#### agents.yaml
Defines the three agents with their roles, goals, and backstories:
- **knowledge_manager**: Senior Knowledge Engineer - handles document ingestion
- **search_planner**: Search Strategy Lead - maps queries to files
- **data_analyst**: Data Retrieval & Reporting Specialist - executes search and synthesizes answers

#### tasks.yaml
Defines the three sequential tasks:
- **ingestion_task**: Parse and index files into vector database
- **search_planning_task**: Create Search Manifest mapping queries to files
- **qa_task**: Retrieve chunks and compose final answer

## Usage

### Basic Usage

```bash
python src/readeragent/main.py
```

The system will prompt you to:
1. Enter your query (e.g., "What are the exam fees for sem 1?")
2. Provide a list of filenames to ingest

### Input Format

The system accepts:
- **Query**: Natural language question or information request
- **Filenames**: List of PDF/image files to ingest (e.g., `['BTech_2nd_year_core_Syllabus.pdf', 'sem1_examfee.pdf']`)
- **Current Year**: Automatically captured from system date

### Example Workflow

1. **Ingestion**: System parses BTech_2nd_year_core_Syllabus.pdf and sem1_examfee.pdf
2. **Planning**: Query "What are exam fees for sem 1?" is routed to sem1_examfee.pdf
3. **QA**: System retrieves relevant fee information and provides structured answer

## Requirements

- Python 3.8+
- CrewAI framework
- Docling (document parsing)
- Qdrant (vector database)
- LangChain text splitters
- Pydantic (data validation)
- python-dotenv (environment configuration)
- AgentOps (monitoring/observability)

## Installation

```bash
# Install dependencies (assumes pyproject.toml exists)
pip install -r requirements.txt

# Or with pip directly
pip install crewai docling qdrant-client langchain pydantic python-dotenv agentops
```

## Key Features

- **Advanced Document Understanding**: Uses Docling with OCR and table detection for accurate text extraction
- **Semantic Search**: Vector embeddings enable finding contextually relevant information regardless of exact keyword matches
- **Intelligent Routing**: Agents automatically determine which documents are relevant to queries
- **Structured Workflow**: Sequential task execution ensures proper context passing between agents
- **Metadata Preservation**: Source filename is tracked for all retrieved chunks, enabling proper attribution
- **Error Handling**: Comprehensive error reporting at each stage of the pipeline

## Development Notes

### Agent Iteration Settings
- **max_rpm**: 5 (requests per minute limit)
- **max_iter**: 3 (maximum iterations per agent)
- **Process**: Sequential (tasks execute in order with context passing)

### Monitoring
The system integrates AgentOps for observability with decorators on agents and tasks:
- `@ao_agent` - Monitor agent execution
- `@ao_task` - Track task completion and outputs

### Future Enhancements
- Add support for additional document formats (Word, Excel, etc.)
- Implement parallel processing for multiple file ingestion
- Add caching layer for frequently accessed chunks
- Extend vector search with hybrid filtering options
- Support for real-time document updates without full re-ingestion

## Troubleshooting

### Common Issues

**"Local directory does not exist"**
- Ensure `LOCAL_FILES_DIR` environment variable points to valid directory containing document files

**"No files found in directory"**
- Verify files exist in the path specified by `LOCAL_FILES_DIR`
- Check file permissions

**Vector search returning no results**
- Ensure documents were successfully ingested (check ingestion_task output)
- Verify collection name in `.env` matches created collection in Qdrant
- Try rephrasing the query for better semantic matching

## Project Status

This is an active project in development. Core functionality for document parsing, semantic search, and multi-agent coordination is implemented and functional.
