# Flex MCP Server

An MCP (Model Context Protocol) server that provides read-only access to the Dalet Flex API, allowing AI assistants like Claude to query and retrieve information from your Flex environment.

## Features

This MCP server provides comprehensive read-only access to Flex objects:

### Asset Operations
- `get_asset` - Get details of a specific asset by ID
- `search_assets` - Search for assets using matrix parameter filters
- `search_assets_fql` - Search for assets using FQL (Flex Query Language) for text search
- `get_asset_metadata` - Get metadata for a specific asset
- `get_asset_annotations` - Get annotations for a specific asset

### Generic Object Search
- `search_objects` - Search ANY object type including:
  - Standard objects (assets, collections, users, etc.)
  - User Defined Objects (UDOs) like Series, Episodes, or custom objects

### Collection Operations
- `get_collections` - Get list of collections
- `get_collection_items` - Get items in a specific collection

### Workflow & Job Operations
- `get_workflows` - Get list of workflow definitions
- `get_job` - Get details of a specific job

### User Operations
- `get_users` - Get list of users

### Utility Operations
- `get_metadata_definition_fields` - Get metadata field definitions
- `test_connection` - Test the connection to Flex API

## Installation

### Prerequisites
- Python 3.8 or higher
- Access to a Dalet Flex instance
- Valid Flex API credentials

### Install from source

```bash
git clone https://github.com/your-username/flex-python-sdk.git
cd flex-python-sdk/mcp-server
pip install -e .
```

### Install from PyPI (when available)

```bash
pip install flex-mcp-server
```

## Configuration

### Environment Variables

Create a `.env` file in the mcp-server directory (copy from `.env.example`):

```bash
FLEX_ENV_URL=https://your-flex-instance.com/api
FLEX_ENV_USERNAME=your-username
FLEX_ENV_PASSWORD=your-password
```

Or export them in your shell:

```bash
export FLEX_ENV_URL="https://your-flex-instance.com/api"
export FLEX_ENV_USERNAME="your-username"
export FLEX_ENV_PASSWORD="your-password"
```

## Usage

### Running the Server Standalone

```bash
flex-mcp
```

### Using with Claude Desktop

1. Add to your Claude Desktop configuration:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "flex": {
      "command": "flex-mcp",
      "env": {
        "FLEX_ENV_URL": "https://your-flex-instance.com/api",
        "FLEX_ENV_USERNAME": "your-username",
        "FLEX_ENV_PASSWORD": "your-password"
      }
    }
  }
}
```

2. Restart Claude Desktop

3. The Flex tools will now be available in your conversations

## Filter Syntax Guide

### Matrix Parameters (search_assets, search_objects)

Filters use semicolon-separated key=value pairs:

**Basic filters:**
- `name=MyAsset` - Exact name match
- `assetType=File` - File or Group
- `fileType=Media` - Media, Image, Text, Archive, etc.
- `status=Active` - Asset status
- `deleted=false` - Exclude deleted assets
- `approved=true` - Only approved assets

**Technical properties (Media/Image):**
- `technicalType=Media` - Filter by technical type
- `format=MOV` - MOV, MP4, MXF, JPEG, PNG, etc.
- `videoCodec=H.264` - H.264, H.265, ProRes, etc.
- `frameRate=25` - Frame rate
- `frameWidth=1920;frameHeight=1080` - Resolution

**Date filters:**
- `created>2024-01-01` - Created after date
- `createdFrom=24 Jun 2021;createdTo=now` - Date range
- `embargoDate=24 Nov 2024` - Embargo date

**Metadata search (requires metadataDefinitionId):**
- `metadata=title:Olympics;metadataDefinitionId=123`
- `metadata=category:Sports;metadata=year:2024;metadataDefinitionId=123`

**Combined filters:**
- `assetType=File;fileType=Media;deleted=false`
- `technicalType=Media;format=MOV;frameRate=25`

### FQL - Flex Query Language (search_assets_fql)

For text search and complex queries:
- `title:Olympics` - Search in title field
- `description:"London 2012"` - Exact phrase search
- `metadata.event:Olympics` - Search in metadata fields
- `title:Olympics AND created > "2024-01-01"` - Complex queries
- `category:Sports OR event:Olympics` - OR conditions

### User Defined Objects (search_objects)

Search custom object types using plural names:
```python
# Search for Series (UDO)
search_objects(plural_name="series", filters="name=MySeries;status=Active")

# Search for Episodes (UDO)
search_objects(plural_name="episodes", filters="season=1;episode=5")
```

## Example Queries

### Asset Searches
```
"Find all media files created this year"
→ search_assets with filters: assetType=File;fileType=Media;created>2024-01-01

"Search for Olympics footage"
→ search_assets_fql with query: title:Olympics OR description:Olympics

"Find ProRes videos at 1080p"
→ search_assets with filters: technicalType=Media;videoCodec=ProRes;frameHeight=1080
```

### UDO Searches
```
"Find all Series with status Active"
→ search_objects with plural_name="series", filters="status=Active"

"Search for Episode 5 of Season 1"
→ search_objects with plural_name="episodes", filters="season=1;episode=5"
```

## Security

- **Read-only access**: This server only performs GET operations
- **Credential security**: Store credentials in environment variables or .env file
- **No write operations**: Prevents accidental modifications to your Flex data
- **Authentication**: Uses Flex API basic authentication

## Development

### Project Structure
```
mcp-server/
├── flex_mcp_server.py    # Main server implementation
├── pyproject.toml        # Package configuration
├── requirements.txt      # Dependencies
├── README.md            # This file
├── .env.example         # Example environment configuration
└── LICENSE              # License file
```

### Adding New Operations

To add new read-only operations:

1. Add the tool definition in `handle_list_tools()`
2. Add the handler in `handle_call_tool()`
3. Implement the operation method (must be read-only)
4. Update this README with the new operation

Example:
```python
types.Tool(
    name="get_taxonomies",
    description="Get list of taxonomies",
    inputSchema={
        "type": "object",
        "properties": {
            "filters": {"type": "string", "description": "Optional filters"}
        }
    }
)
```

## Troubleshooting

### Connection Issues
- Verify your FLEX_ENV_URL includes `/api` suffix
- Check credentials are correct
- Ensure your Flex user has appropriate read permissions
- Use `test_connection` tool to diagnose issues

### Search Issues
- For metadata search, always include `metadataDefinitionId`
- Use exact plural names for UDOs (case-sensitive)
- Check filter syntax - must be key=value pairs
- Use FQL for text search, not matrix parameters

### Common Errors
- `401 Unauthorized` - Check credentials
- `404 Not Found` - Verify object IDs or plural names
- `Invalid filter format` - Use proper matrix parameter syntax

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- GitHub Issues: [your-repo-url]/issues
- Flex Documentation: [Flex API Documentation URL]
- MCP Protocol: https://modelcontextprotocol.io