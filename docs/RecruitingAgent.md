# Recruiting Agent

An intelligent AI-powered recruiting agent built with [CrewAI](https://github.com/joaomdmoura/crewai) that automates the candidate sourcing and hiring process through a multi-agent workflow.

## Overview

The Recruiting Agent uses a sophisticated multi-agent system powered by large language models to:
1. **Extract job requirements** from natural language job descriptions
2. **Search internal databases** for matching candidates
3. **Search externally** on LinkedIn and Google when database results are insufficient
4. **Save qualified candidates** to a PostgreSQL database

The system implements a sequential workflow where each agent specializes in a specific recruiting task with detailed instructions and constraints.

## Project Structure

```
recruitingagent/
├── README.md
├── pyproject.toml                 # Project configuration and dependencies
├── knowledge/
│   └── user_preference.txt       # User profile and preferences
├── src/
│   └── recruitingagent/
│       ├── __init__.py
│       ├── main.py               # Entry point for running the crew
│       ├── crew.py               # Crew definition with agents and tasks
│       ├── config/
│       │   ├── agents.yaml       # Agent role definitions and backstories
│       │   └── tasks.yaml        # Task descriptions and expected outputs
│       ├── pymodels/
│       │   ├── recuirementExtracter.py    # Pydantic schema for job requirements
│       │   └── webSearchOutput.py         # Pydantic schema for candidate data
│       └── tools/
│           ├── __init__.py
│           ├── DBSaverTool.py    # Tool for saving candidates to database
│           └── searchTools/
│               ├── WebsearchTool.py      # Google Custom Search API integration
│               └── DBsearchTool.py       # PostgreSQL database search tool
└── tests/                        # Test directory (empty)
```

## Architecture

### Multi-Agent Workflow

The recruiting system follows a **sequential process** with four specialized agents:

#### 1. **RecurimentExtracter Agent**
- **Role**: Data Extraction Architect
- **Goal**: Transform messy job descriptions into structured JSON data
- **Responsibilities**:
  - Parse job descriptions to extract skills, experience, domain, budget, and location
  - Infer seniority level (Junior, Mid, Senior, Lead) to estimate hourly rates
  - Filter out soft skills and focus on hard technical skills
  - Maintain schema integrity for demographic fields
  - Output structured `RecuirementExtracter` Pydantic model

#### 2. **DBcandidateSearch Agent**
- **Role**: Internal Talent Database Specialist
- **Goal**: Query internal candidate database for matching candidates
- **Responsibilities**:
  - Use `DBsearchTool` to search for candidates matching required skills
  - Filter candidates whose rates exceed budget
  - Return at least 5 candidates or output "THRESHOLD_NOT_MET" trigger
  - Enable conditional execution of the external search agent

#### 3. **CandidateFinder Agent**
- **Role**: External Sourcing Strategist
- **Goal**: Find external candidates on LinkedIn and Google when internal search is insufficient
- **Responsibilities**:
  - Executes only if database search returns < 5 candidates
  - Uses `WebSearchTool` for LinkedIn profile searches
  - Constructs precise search queries: `[Skill 1] + [Skill 2] + [Location]`
  - Assigns match scores (0-10) based on profile fit
  - Outputs `CandidateList` with up to 10 external candidates

#### 4. **CandidateSaver Agent**
- **Role**: Database Transaction Manager
- **Goal**: Persist candidates to the database and report results
- **Responsibilities**:
  - Consolidates all candidates from previous search steps
  - Calls `CandidateSaverTool` exactly once with complete candidate list
  - Ensures database persistence and returns actual database response
  - Prioritizes truth over speed (no hallucination of saves)

### Data Models

#### RecuirementExtracter
```python
{
    "skills": List[str],          # Required technical skills
    "experience": str,            # Years of experience needed
    "domain": str,               # Field of work (Fintech, Healthcare, etc.)
    "budget": str,               # Hourly rate or salary
    "location": str,             # Geographic location
    "gender": str,               # Gender preference (default: "Prefer not to say")
    "age": str                   # Age range (default: "22-30")
}
```

#### Candidate
```python
{
    "name": str,                 # Candidate name
    "profile_link": str,         # LinkedIn profile or web link
    "bio": str,                  # Professional summary from profile
    "skills": List[str],         # Technical skills
    "match_score": int           # Quality match (0-10 scale)
}
```

## Tools

### 1. DBsearchTool
- **Type**: Database Query Tool
- **Database**: PostgreSQL
- **Function**: Searches candidate database for matching skills
- **Input**: List of skills to search
- **Output**: Formatted string with candidate information (name, bio, profile link)
- **Configuration**: Environment variables for database connection

### 2. WebSearchTool
- **Type**: External Web Search Tool
- **Service**: Google Custom Search API
- **Function**: Searches LinkedIn for candidate profiles
- **Input**: Search query (skills + location)
- **Output**: JSON array of candidates with profile links and bios
- **Features**: Filters to LinkedIn profiles only using `site:linkedin.com/in` modifier

### 3. CandidateSaverTool
- **Type**: Database Write Tool
- **Database**: PostgreSQL
- **Function**: Persists candidates to the database
- **Input**: List of candidate objects or JSON string
- **Output**: Database operation status
- **Features**: 
  - Flexible input handling (dict, list, JSON string)
  - Duplicate prevention
  - Skills normalization
  - Transaction-safe operations

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# LLM Configuration
OPENAI_MODEL_NAME=your-model-name
OPENAI_API_BASE=http://localhost:8000/v1

# Database Configuration
DB_HOST=localhost
DB_NAME=recruiting_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432

# Google Search Configuration
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_custom_search_engine_id
```

### Agent Configuration (agents.yaml)

Each agent has defined roles, goals, and backstories that shape their behavior:
- **RecurimentExtracter**: Strict parsing rules, schema validation
- **DBcandidateSearch**: Database expertise, threshold-based filtering
- **CandidateFinder**: Web scraping expertise, budget filtering
- **CandidateSaver**: Database transaction management, integrity verification

### Task Configuration (tasks.yaml)

Tasks define:
- **Description**: Step-by-step execution instructions
- **Expected Output**: Format and content requirements
- **Agent Assignment**: Which agent performs the task
- **Context**: Information from previous tasks
- **Callbacks**: Conditional logic (e.g., trigger external search if DB insufficient)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd recruitingagent
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e .
   ```
   
   Or install directly:
   ```bash
   pip install crewai[tools]==1.6.0
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database setup**
   - Ensure PostgreSQL is running
   - Create database and tables:
   ```sql
   CREATE DATABASE recruiting_db;
   -- Create candidate table with skills array column
   CREATE TABLE candidate (
       id SERIAL PRIMARY KEY,
       name VARCHAR(255),
       bio TEXT,
       profile_link VARCHAR(255),
       skills TEXT[] -- PostgreSQL array type
   );
   ```

## Usage

### Run the Agent

```bash
python src/recruitingagent/main.py
```

The script will prompt you:
```
Enter what message u want to do:
```

Provide a job description, and the agent will:
1. Extract requirements
2. Search the internal database
3. Search LinkedIn if needed
4. Save qualified candidates to the database

### Example Input

```
I need a Senior Python developer with Django and PostgreSQL experience 
for an e-commerce platform. Budget is $150/hour. Must be based in 
San Francisco area.
```

### CLI Commands

The project includes several CLI commands defined in `pyproject.toml`:

```bash
recruitingagent          # Run the crew
run_crew                 # Alias for run
train                    # Train the crew (not fully implemented)
replay                   # Replay crew execution (not fully implemented)
test                     # Test crew execution (not fully implemented)
run_with_trigger         # Run with trigger payload (not fully implemented)
```

## Workflow Execution

### Sequential Process

```
Input Job Description
         ↓
[RecurimentExtracter Agent]
Extract requirements (skills, budget, location, etc.)
         ↓
[DBcandidateSearch Agent]
Search internal database
         ↓
Candidates Found? → YES → [CandidateSaver Agent]
         ↓ NO                    ↓
         └─→ [CandidateFinder Agent]
             Search LinkedIn/Google
                    ↓
             [CandidateSaver Agent]
             Save all candidates to DB
                    ↓
              Return Results
```

### Conditional Logic

- **DBcandidate_search_task** triggers `CandidateFinder` only if result contains "THRESHOLD_NOT_MET"
- **candidate_finding_task** only executes if internal search insufficient
- **candidate_saving_task** consolidates results from all sources before saving

## Key Features

✅ **Multi-Agent Architecture**: Specialized agents for different recruiting tasks  
✅ **Smart Requirement Extraction**: Structured parsing of unstructured job descriptions  
✅ **Database-First Strategy**: Searches internal talent pool before external sources  
✅ **Conditional Execution**: External search only when database threshold not met  
✅ **Budget Filtering**: Candidates filtered by hourly rate constraints  
✅ **Skill Matching**: Hard-skills focused (no soft-skills or buzzwords)  
✅ **LLM Agnostic**: Uses configurable LLM base URL and model  
✅ **Schema Validation**: Pydantic models ensure data integrity  
✅ **PostgreSQL Integration**: Persistent storage with array-type skills  
✅ **Monitoring**: AgentOps integration for observability (optional)

## Dependencies

- **crewai[tools]==1.6.0**: CrewAI framework with built-in tools
- **psycopg2**: PostgreSQL database adapter
- **pydantic**: Data validation using Python type annotations
- **google-api-python-client**: Google Custom Search API
- **python-dotenv**: Environment variable management
- **agentops**: Optional observability and monitoring

## Limitations & Future Improvements

### Current Limitations
- External search limited to LinkedIn via Google (requires Google Custom Search API)
- No caching of search results
- No deduplication across database and web results
- Task implementations for train/replay/test are not fully implemented
- No authentication for API endpoints

### Potential Improvements
- [ ] Add caching layer for search results
- [ ] Implement result deduplication
- [ ] Add more search sources (Indeed, GitHub, company websites)
- [ ] Implement candidate ranking algorithms
- [ ] Add email integration for candidate outreach
- [ ] Build REST API for integration with ATS systems
- [ ] Add webhook support for external events
- [ ] Implement conversation memory for multi-turn interactions
- [ ] Add data export features (CSV, JSON)

## Development

### Project Dependencies Location
- Configuration: [pyproject.toml](pyproject.toml)
- Agent Definitions: [src/recruitingagent/config/agents.yaml](src/recruitingagent/config/agents.yaml)
- Task Definitions: [src/recruitingagent/config/tasks.yaml](src/recruitingagent/config/tasks.yaml)
- Main Crew Logic: [src/recruitingagent/crew.py](src/recruitingagent/crew.py)

### Testing

Tests are placeholder only. To test the agent:

```bash
# Test with a sample job description
python src/recruitingagent/main.py << EOF
Senior Full Stack Developer needed for FinTech startup. 
5+ years exp. React, Node.js, PostgreSQL required.
$120-150/hr. Remote.
EOF
```

## Author

Created as part of the Kins Agents project.

## License

See LICENSE file for details.

## References

- [CrewAI Documentation](https://docs.crewai.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Google Custom Search API](https://developers.google.com/custom-search)
- [Pydantic Documentation](https://docs.pydantic.dev/)
