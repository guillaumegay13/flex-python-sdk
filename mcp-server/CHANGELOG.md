# Changelog

All notable changes to the Flex MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-08-14

### Added
- Initial release of Flex MCP Server
- Read-only access to Dalet Flex API
- Asset search with matrix parameters and FQL
- Generic object search supporting UDOs
- Collection, workflow, job, and user operations
- Metadata and annotation retrieval
- Connection testing functionality
- Comprehensive documentation and examples

### Security
- All operations are read-only to prevent accidental modifications
- Credentials stored securely in environment variables
- No sensitive information logged