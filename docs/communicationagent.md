# communicationagent

One-line description: A lightweight communication agent package providing tools and configuration for sending and reviewing messages across channels (email, WhatsApp) and searching a local DB.

## Overview

The `communicationagent` package contains agent entry points, supporting models, and a set of tools for multi-channel communication (email, WhatsApp) and search/review utilities. It centralizes configuration under `config/` and exposes small, testable modules under `tools/` and `pyModels/`.

Key capabilities:
- Agent entry point and orchestration
- Email and WhatsApp sending utilities
- DB search utility for knowledge lookups
- Lightweight extraction model in `pyModels`

## Project Structure

```
communicationagent/
├── README.md
├── TEMPLATE.md
├── knowledge/
├── src/
│   └── communicationagent/
│       ├── __init__.py
│       ├── main.py
│       ├── crew.py
│       ├── config/
│       │   ├── agents.yaml
│       │   └── tasks.yaml
│       ├── pyModels/
│       │   └── extracter.py
│       └── tools/
│           ├── dbSearch.py
│           ├── emailTool.py
│           ├── reviewTool.py
│           └── whatsappTool.py
└── tests/
```

## Architecture

### System Design

The codebase is organized as a small Python package (`src/communicationagent`) with a clear separation between configuration, models, and tools. `main.py` provides the entry point and high-level orchestration; `crew.py` groups agent/team logic; `tools/` implements channel-specific capabilities.

### Core Components

#### Entry / Orchestration
- **Purpose**: Launch and coordinate agent tasks.
- **Key Responsibilities**:
  - Parse configuration in `config/`
  - Start agent flows from `main.py`

#### Tools
- **Purpose**: Channel-specific send/search/review utilities.
- **Key Responsibilities**:
  - `emailTool.py`: send and format emails
  - `whatsappTool.py`: format/send WhatsApp messages
  - `dbSearch.py`: search a local DB/knowledge store
  - `reviewTool.py`: evaluate message content or results

#### Models
- **Purpose**: Lightweight extraction/parsing utilities.
- **Key Responsibilities**:
  - `extracter.py`: provides content extraction helpers used by tools or agents

### Data Models

Representative structures (examples):

```python
{
    "message": str,
    "recipient": str,
    "metadata": dict
}
```

## Configuration

### Environment Variables

Create a `.env` file in your environment with any API keys or credentials required by external services used by the tools (SMTP creds, WhatsApp API keys, DB paths).

### Configuration Files

- **Agents configuration**: [src/communicationagent/config/agents.yaml](src/communicationagent/config/agents.yaml)
- **Tasks configuration**: [src/communicationagent/config/tasks.yaml](src/communicationagent/config/tasks.yaml)

## Installation

1. Clone the repository and create a virtual environment

```bash
git clone <repo-url>
cd communicationagent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # if present
```

2. Configure environment and config files

```bash
# copy or edit .env as needed
```

## Usage

Run the package entry point (if `main.py` exposes a runnable CLI or function):

```bash
python src/communicationagent/main.py
```

Key modules:
- Entry point: [src/communicationagent/main.py](src/communicationagent/main.py)
- Agent group: [src/communicationagent/crew.py](src/communicationagent/crew.py)
- Tools directory: [src/communicationagent/tools](src/communicationagent/tools)

## Features

- Basic multi-channel sending utilities (email, WhatsApp)
- Local DB search helper for knowledge lookups
- Message review tools
- Simple extraction model for parsing content

## Dependencies

List dependencies in your project packaging (`pyproject.toml` or `requirements.txt`). If none present, add packages required for SMTP, HTTP requests, or YAML parsing (e.g., `PyYAML`, `requests`).

## API Reference

See the following modules for functionality and entry functions:

- `main.py`: bootstrap and orchestration
- `crew.py`: team/agent utilities
- `tools/emailTool.py`: email helper functions
- `tools/whatsappTool.py`: WhatsApp helper functions
- `pyModels/extracter.py`: extraction helpers

## Workflow / Execution Flow

1. Start the agent from `main.py`.
2. `main` reads config from `config/` and initializes required tools.
3. Tools perform sending/search/review operations as configured.

## Limitations & Known Issues

- This repo snapshot focuses on utilities and lacks integration tests for external services.
- Sensitive credentials must be provided separately via environment variables.

## Future Improvements

- Add integration tests and CI
- Provide example `.env` and `.env.example`
- Add clearer CLI arguments and a small README usage example in `src/communicationagent/`.

## Development

- Main logic: [src/communicationagent/main.py](src/communicationagent/main.py)
- Configuration: [src/communicationagent/config](src/communicationagent/config)
- Tools: [src/communicationagent/tools](src/communicationagent/tools)

### Running Tests

Run tests under `tests/` if present:

```bash
pytest tests/
```

## Troubleshooting

- If sending fails, confirm SMTP/WhatsApp API credentials and network access.
- If YAML parsing fails, validate the YAML files under `src/communicationagent/config/`.

## References

- Project README: [README.md](README.md)

## Changelog

Initial documentation generated from TEMPLATE.md and repository contents.

## Author(s)

- Project owner / contributors (see repo history)

---

**Last Updated**: 2026-02-07
