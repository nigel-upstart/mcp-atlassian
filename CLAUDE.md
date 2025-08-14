# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Setup and Installation
```bash
# Install dependencies using uv
uv sync
uv sync --frozen --all-extras --dev

# Activate virtual environment (macOS/Linux)
source .venv/bin/activate

# Activate virtual environment (Windows)
.venv\Scripts\activate.ps1

# Set up pre-commit hooks
pre-commit install
```

### Testing
```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=mcp_atlassian

# Run specific test module
uv run pytest tests/unit/jira/test_issues.py

# Run tests with real Atlassian data (requires .env setup)
./scripts/test_with_real_data.sh --api

# Run tests with write operations (modifies data)
./scripts/test_with_real_data.sh --api --with-write-tests

# Run model validation tests only
./scripts/test_with_real_data.sh --models

# Run tests with filter pattern
./scripts/test_with_real_data.sh --api -k "test_jira_get_issue"
```

### Code Quality and Linting
```bash
# Run all pre-commit hooks
pre-commit run --all-files

# Format code with ruff
uv run ruff format

# Lint code with ruff
uv run ruff check

# Type check with mypy
uv run mypy src/
```

### Running the Server
```bash
# Run with Docker (recommended)
docker run --rm -i --env-file .env ghcr.io/sooperset/mcp-atlassian:latest

# Run locally for development
uv run mcp-atlassian

# Run with verbose logging
uv run mcp-atlassian -vv

# Run OAuth setup wizard
uv run mcp-atlassian --oauth-setup

# Run HTTP server with SSE transport
uv run mcp-atlassian --transport sse --port 9000

# Run HTTP server with streamable-http transport
uv run mcp-atlassian --transport streamable-http --port 9000
```

## Architecture Overview

### Project Structure
- **`src/mcp_atlassian/`**: Main application code
  - **`servers/`**: FastMCP server implementations
    - `main.py`: Main server with tool filtering and middleware
    - `jira.py`: Jira-specific MCP server
    - `confluence.py`: Confluence-specific MCP server
  - **`jira/`**: Jira integration modules
    - `client.py`: Jira API client wrapper
    - `issues.py`, `comments.py`, etc.: Feature-specific modules
    - `forms.py`: ProForma forms handling (NEW feature)
  - **`confluence/`**: Confluence integration modules
    - `client.py`: Confluence API client wrapper
    - `pages.py`, `comments.py`, etc.: Feature-specific modules
  - **`models/`**: Pydantic data models for API responses
  - **`utils/`**: Shared utilities (auth, logging, environment)

### Key Components

#### Server Architecture
- **FastMCP Framework**: Uses FastMCP for MCP protocol implementation
- **Multi-service Support**: Handles both Jira and Confluence in single server
- **Tool Filtering**: Dynamic tool availability based on configuration and auth
- **Multi-transport**: Supports stdio, SSE, and streamable-http transports
- **Authentication Middleware**: Handles OAuth, API tokens, and PAT authentication

#### Authentication Flow
1. **Environment-based Config**: Server loads auth from environment variables
2. **User Token Middleware**: Extracts Bearer/Token headers for per-request auth
3. **Multi-cloud Support**: X-Atlassian-Cloud-Id header for instance routing
4. **Fallback Strategy**: Uses server config if user tokens not provided

#### Tool Organization
- **Service-specific Tools**: Prefixed with `jira_` or `confluence_`
- **Read/Write Classification**: Tools tagged for read-only mode filtering
- **Dynamic Registration**: Tools registered based on service availability
- **Context Injection**: Service configs injected via lifespan context

### Configuration Management

#### Environment Variables
- **Service URLs**: `JIRA_URL`, `CONFLUENCE_URL`
- **Authentication**: API tokens, PATs, OAuth credentials
- **Filtering**: `JIRA_PROJECTS_FILTER`, `CONFLUENCE_SPACES_FILTER`
- **Behavior**: `READ_ONLY_MODE`, `ENABLED_TOOLS`
- **Logging**: `MCP_VERBOSE`, `MCP_VERY_VERBOSE`, `MCP_LOGGING_STDOUT`

#### Authentication Methods
1. **API Tokens** (Cloud): Username + API token
2. **Personal Access Tokens** (Server/DC): Token-based auth
3. **OAuth 2.0** (Cloud): Full OAuth flow with refresh tokens

### Testing Framework

#### Test Structure
- **Unit Tests**: `tests/unit/` - Component-level testing
- **Integration Tests**: `tests/integration/` - Cross-service testing
- **Real API Tests**: `tests/test_real_api_validation.py` - Live API validation
- **Fixture System**: Enhanced factory-based test data generation

#### Test Categories
- **Mock Tests**: Use `tests/fixtures/` for static mock data
- **Factory Tests**: Use `tests/utils/factories.py` for dynamic data
- **Real Data Tests**: Require `.env` setup with actual Atlassian credentials

## Development Guidelines

### Code Style Requirements
- **Line Length**: 88 characters (ruff configured)
- **Type Annotations**: Required for all functions and methods
- **Import Organization**: Follow ruff import sorting rules
- **Docstrings**: Google-style format for all public APIs

### Error Handling Patterns
- **Service Errors**: Wrap Atlassian API exceptions in custom exception types
- **Authentication**: Graceful degradation when auth fails
- **Tool Availability**: Tools filtered out rather than failing when unconfigured

### New Feature Development
1. **Add Models**: Create Pydantic models in `models/` for API responses
2. **Implement Client Methods**: Add API calls in appropriate `client.py`
3. **Create Tools**: Register MCP tools in service-specific servers
4. **Add Tests**: Unit tests for logic, integration tests for workflows
5. **Update Documentation**: Tool descriptions and examples

### ProForma Forms Feature (Recent Addition)
The repository includes support for Atlassian ProForma forms:
- **`jira/forms.py`**: Core forms handling logic
- **`models/jira/forms.py`**: Form data models
- **Form Tools**: `jira_get_issue_forms`, `jira_reopen_form`, `jira_submit_form`
- **Field Integration**: Form fields linked to Jira custom fields

### Common Pitfalls
- **Authentication Context**: Always check if service configs are available before tool execution
- **Rate Limiting**: Atlassian APIs have rate limits - implement backoff strategies
- **Environment Loading**: dotenv loading happens in `__init__.py`, respect precedence
- **Docker Context**: When running in Docker, paths and environment handling differ

### Debugging Tips
- **Enable Verbose Logging**: Use `-vv` flag or `MCP_VERY_VERBOSE=true`
- **MCP Inspector**: Use `npx @modelcontextprotocol/inspector` for tool testing
- **Real API Testing**: Use `./scripts/test_with_real_data.sh` for API validation
- **Header Debugging**: Custom headers are logged with values masked for security
