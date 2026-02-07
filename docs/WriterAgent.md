# writeragent

A small agent-based writer utility that extracts and processes content from a variety of file formats (DOCX, PDF, Excel, plain text) and provides configurable agent/task definitions for automated workflows.

## Overview

writeragent provides lightweight tools and models to extract content from files, apply simple processing pipelines, and orchestrate tasks via YAML-configured agents. It's intended as a foundation for building automated content-extraction and document-processing agents.

Key capabilities:
- Extract content from DOCX, PDF, Excel, and text files
- Configurable agents and tasks via YAML files
- Small Python utilities for reading and writing various file types
- Simple pluggable model and tool layout for extension

## Project Structure

```
writeragent/
├── TEMPLATE.md
├── README.md                 # This file
├── knowledge/                # Knowledge base files
├── src/
│   └── writeragent/
│       ├── crews.py          # Agent/crew orchestration utilities
│       ├── flow.py           # Flow control and task orchestration
│       ├── main.py           # Entry point / example runner
│       ├── config/           # Per-format agent/task YAML configs
│       │   ├── docx/
│       │   │   ├── agents.yaml
       │   │   └── tasks.yaml
       │   ├── excel/
       │   │   ├── agents.yaml
       │   │   └── tasks.yaml
       │   ├── pdf/
       │   │   ├── agents.yaml
       │   │   └── tasks.yaml
       │   └── text/
       │           ├── agents.yaml
       │           └── tasks.yaml
       ├── pymodels/          # small model helpers (e.g., ContentExtracter)
       │   ├── ContentExtracter.py
       │   └── report.css
       └── tools/             # File reading/writing utilities
           ├── DOCXFileTool.py
           ├── ExcelFileTool.py
           ├── PDFFileTool.py
           ├── TextFileTool.py
           └── UniversalFileWritingTool.py
└── tests/                    # Tests (if any)
```

## Quick Start

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies (if you maintain a requirements file or pyproject):

```bash
pip install -r requirements.txt  # or use your project's install method
```

3. Run the example entrypoint:

```bash
python src/writeragent/main.py
```

Note: `main.py` is a simple runner; adapt or import `flow.py` / `crews.py` for programmatic use.

## Configuration

Agent and task configuration lives in `src/writeragent/config/` organized by file format. Each subfolder contains two YAML files: `agents.yaml` and `tasks.yaml` which define agent behavior and task pipelines.

Examples:
- `src/writeragent/config/docx/agents.yaml`
- `src/writeragent/config/pdf/tasks.yaml`

## Key Files

- `src/writeragent/main.py`: Example runner / entrypoint.
- `src/writeragent/flow.py`: Orchestration of flows and task sequencing.
- `src/writeragent/crews.py`: Higher-level agent/crew management.
- `src/writeragent/tools/*`: File I/O helper tools for DOCX, PDF, Excel, and text.
- `src/writeragent/pymodels/ContentExtracter.py`: Model/helper for extracting content.

## Testing

Run tests with:

```bash
pytest tests/
```

If the project has no test dependencies declared yet, add them to `requirements.txt` or `pyproject.toml`.

## Development Notes

- The code is intentionally small and modular: add new file-format tools under `src/writeragent/tools` and register/describe tasks in the `config` YAML files.
- Consider adding a `pyproject.toml` or `requirements.txt` and a top-level `setup.py` if packaging or editable installs are needed.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Open a pull request with a clear description

## License

Add a `LICENSE` file to the repository and update this section accordingly.

## Next Steps (Suggested)

- Add dependency manifest (`requirements.txt` or `pyproject.toml`).
- Add examples or CLI flags to `main.py` demonstrating common workflows.
- Add unit tests for `tools` and `pymodels`.

---

Last updated: 2026-02-07
