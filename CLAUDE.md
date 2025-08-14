# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Installation and Setup
```bash
# Install the package in development mode
pip install -e .

# Install from PyPI
pip install flex-sdk

# Install dependencies
pip install -r requirements.txt
```

### Building and Distribution
```bash
# Build the package
python -m build

# Upload to PyPI (requires authentication)
python -m twine upload dist/*
```

### Testing
Note: No test framework is currently set up. When implementing tests, consider using pytest with the following structure:
- Create a `tests/` directory
- Add test files following the pattern `test_*.py`
- Consider adding integration tests that mock the Flex API responses

## Architecture Overview

### Package Structure
The Flex Python SDK is a client library for interacting with the Dalet Flex API. Key components:

1. **FlexApiClient** (`src/flex/flex_api_client.py`): Main API client class
   - Handles authentication using basic auth
   - Provides methods for all Flex API endpoints
   - Implements pagination for large result sets
   - Supports parallel fetching for improved performance

2. **Data Models** (`src/flex/flex_objects.py`): Object representations
   - All API responses are wrapped in Python objects
   - Nested objects are automatically instantiated
   - Key models: Asset, Collection, Workflow, Job, User, Annotation, Taxonomy

3. **Additional Clients**:
   - `account_client.py`: Account-specific operations
   - `account_property_client.py`: Account property management

### Key Design Patterns

1. **Pagination Handling**: 
   - Automatic recursive pagination for results > 100 items
   - Special handling for results > 10,000 with date-based pagination
   - Parallel fetching available via `get_assets_parallel()` and `get_jobs()`

2. **Error Handling**:
   - All API errors are wrapped in generic Exceptions
   - HTTP status codes are checked with `raise_for_status()`

3. **Authentication**:
   - Uses environment variables: `FLEX_ENV_URL`, `FLEX_ENV_USERNAME`, `FLEX_ENV_PASSWORD`
   - Basic authentication with base64 encoding

### Common Workflows

1. **Asset Operations**:
   - Get assets with filters: `get_assets()`, `get_assets_parallel()`
   - Update metadata: `set_asset_metadata()`
   - Manage keyframes, annotations, children

2. **Job Management**:
   - Create jobs: `create_job()`
   - Monitor status: `get_job()`, `get_job_history()`
   - Retry failed jobs: `retry_job()`

3. **Collection Management**:
   - CRUD operations on collections and items
   - Batch updates supported

4. **Taxonomy Operations**:
   - Create hierarchical taxonomies with taxons
   - URL encoding handled for special characters

### Important Notes

- The SDK increases Python's recursion limit to 1500 for deep pagination
- All timestamps are in microseconds
- Content-Type header is set to `application/vnd.nativ.mio.v1+json`
- The SDK is designed for Dalet Flex version that uses this API format