# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a multi-modal content analysis framework built with Python that can analyze various content types including URLs, images, code, and text. It uses LangGraph for workflow orchestration and integrates with multiple AI services (OpenAI, Google Gemini, Alibaba Qwen).

## Key Components

1. **Core Architecture**: Uses LangGraph to define a workflow with input, analysis, summary, and output nodes
2. **Content Analyzers**: Specialized analyzers for different content types (URL, Image, Code)
3. **API Server**: Flask-based REST API for external access
4. **Configuration**: Environment-based configuration for API keys and settings

## Common Development Commands

### Setup and Installation
```bash
uv sync  # Install dependencies
```

### Running the Application
```bash
# Start the API server
uv run python api_server.py

# Run the interactive CLI
uv run python main.py

# Run tests
uv run python test_api.py
```

### Testing the API
```bash
# Health check
curl http://localhost:8888/health

# Analyze content
curl -X POST http://localhost:8888/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "content": "def hello(): print(\"Hello World\")",
    "content_type": "code",
    "context": "Python"
  }'
```

## Codebase Structure

- `api_server.py` - Main Flask API server
- `main.py` - Interactive CLI application
- `multimodal_agent.py` - Main agent orchestration
- `analyzers.py` - Content-specific analysis implementations
- `config.py` - Configuration management
- `graph/` - LangGraph workflow implementation
  - `state.py` - State definitions
  - `nodes.py` - Workflow nodes
  - `workflow.py` - Workflow orchestration
- `test_api.py` - API integration tests

## Development Notes

- Uses uv for dependency management and Python version control
- Requires Python 3.12+
- API keys configured in `.env` file
- Supports OpenAI, Google Gemini, and Alibaba Qwen APIs
- Content analysis results include summaries, key points, and confidence scores