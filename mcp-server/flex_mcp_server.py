#!/usr/bin/env python3
"""
MCP Server for Dalet Flex API - Read-only operations

Asset Search Matrix Parameters:
The Flex API uses matrix parameters for filtering assets. These are semicolon-separated
key=value pairs appended to the API endpoint. Common parameters include:

Basic Properties:
- name: Asset name (exact match by default, use exactNameMatch=false for partial)
- assetType: File | Group
- fileType: Media | Image | Text | Archive | Subtitle | etc.
- technicalType: Media | Image | Archive
- status: Active | Inactive | etc.
- deleted: true | false | all (default: false)
- approved: true | false | all

Technical Properties (for Media/Image):
- format: MOV | MP4 | MXF | JPEG | PNG | etc.
- videoCodec: H.264 | H.265 | ProRes | etc.
- audioCodec: AAC | MP3 | PCM | etc.
- frameRate, frameWidth, frameHeight, bitRate, duration, etc.

Date Filters:
- created/modified with operators: >, <, =
- createdFrom/createdTo, modifiedFrom/modifiedTo
- embargoDate, expiryDate, publishedFrom/publishedTo

Metadata Search:
- metadata=fieldname:value (MUST include metadataDefinitionId)
- metadataDefinitionId=123 (required for metadata searches)

Example filter strings:
- "assetType=File;fileType=Media;deleted=false"
- "technicalType=Media;format=MOV;frameRate=25"
- "metadata=title:Olympics;metadata=year:2024;metadataDefinitionId=123"

Generic Object Search:
The search_objects tool can search ANY object type including:
- Standard objects: assets, collections, users, etc. (use object_type parameter)
- User Defined Objects (UDOs): series, episodes, etc. (use plural_name parameter)
This uses the get_objects_by_filters() method which provides a unified interface
for all Flex object types.
"""

import os
import sys
import json
import asyncio
import logging
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.types as types
import mcp.server.stdio

# Add parent directory to path to import flex SDK
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flex.flex_api_client import FlexApiClient
from flex.flex_objects import Asset, Collection, Workflow, Job, User, Annotation

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FlexMCPServer:
    def __init__(self):
        self.server = Server("flex-mcp-server")
        self.flex_client = None
        self._setup_handlers()
        
    def _setup_handlers(self):
        """Register all handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List all available tools"""
            return [
                types.Tool(
                    name="get_asset",
                    description="Get details of a specific asset by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "asset_id": {"type": "string", "description": "The ID of the asset to retrieve"},
                            "include_metadata": {"type": "boolean", "description": "Whether to include metadata in the response", "default": False}
                        },
                        "required": ["asset_id"]
                    }
                ),
                types.Tool(
                    name="search_assets",
                    description="Search for assets using Flex API matrix parameter filters. Filters use semicolon-separated key=value pairs. Common filters: name, assetType, fileType, status, created/modified dates, metadata fields, technical properties (frameRate, format, etc.). Note: You can also use 'search_objects' with object_type='assets' for the same result.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filters": {
                                "type": "string", 
                                "description": "Matrix parameter filter string. SYNTAX: 'param1=value1;param2=value2'. COMMON FILTERS: name=MyAsset, assetType=File|Group, fileType=Media|Image|Text|Archive, status=Active, technicalType=Media|Image|Archive, format=MOV|MP4|MXF|JPEG|PNG, videoCodec=H.264|H.265|ProRes, audioCodec=AAC|MP3|PCM, frameRate=25|29.97|30, created>2024-01-01, modified<2024-12-31, createdFrom=24 Jun 2021, createdTo=now, metadata=fieldname:value;metadataDefinitionId=123 (REQUIRED for metadata), embargoDate=24 Nov 2024, expiryDate=24 Nov 2024, variant=Original|Proxy, managed=true|false, deleted=false|all, approved=true|false|all. OPERATORS: = (exact match), > (greater than), < (less than), != (not equal). DATE FORMATS: '24 Jun 2021', '24 Jun 2021 10:48:41', '24 Jun 2021 10:48:41 +0200', 'now'. ARRAY VALUES: Use multiple filters with same key or comma-separated. For comprehensive list see API docs."
                            },
                            "limit": {"type": "integer", "description": "Maximum number of results to return (max 1000)", "default": 100}
                        },
                        "required": ["filters"]
                    }
                ),
                types.Tool(
                    name="get_collections",
                    description="Get list of collections",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filters": {"type": "string", "description": "Optional filter string"}
                        }
                    }
                ),
                types.Tool(
                    name="get_collection_items",
                    description="Get items in a specific collection",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "collection_uuid": {"type": "string", "description": "UUID of the collection"}
                        },
                        "required": ["collection_uuid"]
                    }
                ),
                types.Tool(
                    name="get_workflows",
                    description="Get list of workflow definitions",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filters": {"type": "string", "description": "Optional filter string"}
                        }
                    }
                ),
                types.Tool(
                    name="get_job",
                    description="Get details of a specific job",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "job_id": {"type": "string", "description": "The ID of the job"}
                        },
                        "required": ["job_id"]
                    }
                ),
                types.Tool(
                    name="get_asset_metadata",
                    description="Get metadata for a specific asset",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "asset_id": {"type": "string", "description": "The ID of the asset"}
                        },
                        "required": ["asset_id"]
                    }
                ),
                types.Tool(
                    name="get_users",
                    description="Get list of users",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filters": {"type": "string", "description": "Optional filter string"}
                        }
                    }
                ),
                types.Tool(
                    name="get_asset_annotations",
                    description="Get annotations for a specific asset",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "asset_id": {"type": "string", "description": "The ID of the asset"},
                            "limit": {"type": "integer", "description": "Maximum number of annotations to return", "default": 100}
                        },
                        "required": ["asset_id"]
                    }
                ),
                types.Tool(
                    name="search_assets_fql",
                    description="Search for assets using FQL (Flex Query Language) for more complex queries including text search",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "FQL query string. Examples: 'title:Olympics', 'description:\"London 2012\"', 'title:Olympics AND created > \"2024-01-01\"', 'metadata.category:Sports OR metadata.event:Olympics'. Use this for text searches and complex queries."
                            },
                            "limit": {"type": "integer", "description": "Maximum number of results to return", "default": 100}
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="get_metadata_definition_fields",
                    description="Get metadata definition fields to find metadataDefinitionId values needed for metadata searches",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "metadata_definition_id": {
                                "type": "string",
                                "description": "The ID of the metadata definition to inspect"
                            }
                        },
                        "required": ["metadata_definition_id"]
                    }
                ),
                types.Tool(
                    name="test_connection",
                    description="Test the connection to Flex API and verify authentication",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="search_objects",
                    description="Search for any object type (assets, UDOs like Series, etc.) using the generic objects endpoint. Use plural_name for UDOs.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "object_type": {
                                "type": "string",
                                "description": "For standard objects: 'assets', 'collections', 'users', etc. For UDOs, leave empty and use plural_name instead."
                            },
                            "plural_name": {
                                "type": "string",
                                "description": "For User Defined Objects (UDOs), use the plural name (e.g., 'series', 'episodes', 'myCustomObjects'). This overrides object_type."
                            },
                            "filters": {
                                "type": "string",
                                "description": "Matrix parameter filter string. Same syntax as search_assets: 'param1=value1;param2=value2'. For UDOs, you can filter by custom fields."
                            },
                            "limit": {"type": "integer", "description": "Maximum number of results to return", "default": 100},
                            "include_data": {"type": "boolean", "description": "Whether to include object data/metadata in the response", "default": False}
                        },
                        "required": ["filters"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict | None
        ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            """Handle tool execution"""
            if not self.flex_client:
                raise ValueError("Flex client not initialized. Please set FLEX_ENV_URL, FLEX_ENV_USERNAME, and FLEX_ENV_PASSWORD environment variables.")
            
            try:
                if name == "get_asset":
                    return await self._get_asset(arguments or {})
                elif name == "search_assets":
                    return await self._search_assets(arguments or {})
                elif name == "get_collections":
                    return await self._get_collections(arguments or {})
                elif name == "get_collection_items":
                    return await self._get_collection_items(arguments or {})
                elif name == "get_workflows":
                    return await self._get_workflows(arguments or {})
                elif name == "get_job":
                    return await self._get_job(arguments or {})
                elif name == "get_asset_metadata":
                    return await self._get_asset_metadata(arguments or {})
                elif name == "get_users":
                    return await self._get_users(arguments or {})
                elif name == "get_asset_annotations":
                    return await self._get_asset_annotations(arguments or {})
                elif name == "search_assets_fql":
                    return await self._search_assets_fql(arguments or {})
                elif name == "get_metadata_definition_fields":
                    return await self._get_metadata_definition_fields(arguments or {})
                elif name == "test_connection":
                    return await self._test_connection(arguments or {})
                elif name == "search_objects":
                    return await self._search_objects(arguments or {})
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Error executing tool {name}: {str(e)}")
                return [types.TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
    
    async def _get_asset(self, arguments: dict) -> list[types.TextContent]:
        """Get details of a specific asset by ID"""
        asset_id = arguments.get("asset_id")
        include_metadata = arguments.get("include_metadata", False)
        
        asset = self.flex_client.get_asset(asset_id, include_metadata)
        
        result = {
            "id": asset.id,
            "uuid": asset.uuid,
            "name": asset.name,
            "title": asset.title,
            "description": asset.description,
            "type": asset.type,
            "status": asset.status,
            "created": asset.created,
            "lastModified": asset.lastModified,
        }
        
        if hasattr(asset, 'metadata') and asset.metadata:
            result["metadata"] = asset.metadata
            
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    async def _search_assets(self, arguments: dict) -> list[types.TextContent]:
        """Search for assets using matrix parameter filters
        
        Matrix parameters are Flex API's way of filtering results. They use semicolon-separated
        key=value pairs that correspond to asset properties and metadata fields.
        """
        filters = arguments.get("filters")
        limit = arguments.get("limit", 100)
        
        # Validate filter format
        if filters and not any(op in filters for op in ['=', '>', '<', '!=', ':']):
            error_msg = f"Invalid filter format: '{filters}'\n\n"
            error_msg += "Filters must use matrix parameter syntax (key=value pairs), not free text search.\n\n"
            error_msg += "COMMON EXAMPLES:\n"
            error_msg += "Basic filters:\n"
            error_msg += "- 'name=MyAsset' (exact name match)\n"
            error_msg += "- 'assetType=File' (File or Group)\n"
            error_msg += "- 'fileType=Media' (Media, Image, Text, Archive, etc.)\n"
            error_msg += "- 'status=Active'\n"
            error_msg += "- 'deleted=false' (exclude deleted assets)\n"
            error_msg += "- 'approved=true' (only approved assets)\n\n"
            error_msg += "Technical properties (for Media/Image assets):\n"
            error_msg += "- 'technicalType=Media' (then use media-specific filters)\n"
            error_msg += "- 'format=MOV' (MOV, MP4, MXF, etc.)\n"
            error_msg += "- 'videoCodec=H.264' (H.264, H.265, ProRes, etc.)\n"
            error_msg += "- 'frameRate=25' (25, 29.97, 30, etc.)\n"
            error_msg += "- 'frameWidth=1920;frameHeight=1080' (resolution)\n\n"
            error_msg += "Date filters:\n"
            error_msg += "- 'created>2024-01-01' (created after date)\n"
            error_msg += "- 'createdFrom=24 Jun 2021;createdTo=now' (date range)\n"
            error_msg += "- 'embargoDate=24 Nov 2024' (embargo date)\n\n"
            error_msg += "Multiple filters:\n"
            error_msg += "- 'assetType=File;fileType=Media;deleted=false'\n\n"
            error_msg += "Metadata search (REQUIRES metadataDefinitionId):\n"
            error_msg += "- 'metadata=title:Olympics;metadataDefinitionId=123'\n"
            error_msg += "- 'metadata=category:Sports;metadata=year:2024;metadataDefinitionId=123'\n\n"
            error_msg += "For free text search across all fields, use 'search_assets_fql' tool instead."
            raise ValueError(error_msg)
        
        try:
            # The flex_client.get_assets() method expects matrix parameters as a string
            # Format: "param1=value1;param2=value2;param3=value3"
            # The SDK will append these to the API URL as matrix parameters
            assets = self.flex_client.get_assets(filters, offset=0)
            assets = assets[:limit]
            
            results = []
            for asset in assets:
                results.append({
                    "id": asset.id,
                    "name": asset.name,
                    "title": asset.title,
                    "type": asset.type,
                    "status": asset.status,
                    "created": asset.created,
                })
            
            # Include the actual filter string in the response for debugging
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "count": len(results),
                    "filters": filters,
                    "assets": results
                }, indent=2)
            )]
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg:
                error_msg += "\n\nThis might be due to invalid filter syntax. "
                error_msg += "Make sure to use proper matrix parameter format (key=value;key2=value2)."
            raise Exception(error_msg)
    
    async def _get_collections(self, arguments: dict) -> list[types.TextContent]:
        """Get list of collections"""
        filters = arguments.get("filters")
        
        collections = self.flex_client.get_collections(filters)
        
        results = []
        for collection in collections:
            results.append({
                "id": collection.id,
                "uuid": collection.uuid,
                "name": collection.name,
                "description": collection.description if hasattr(collection, 'description') else None,
                "created": collection.created if hasattr(collection, 'created') else None,
            })
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "count": len(results),
                "collections": results
            }, indent=2)
        )]
    
    async def _get_collection_items(self, arguments: dict) -> list[types.TextContent]:
        """Get items in a specific collection"""
        collection_uuid = arguments.get("collection_uuid")
        
        items = self.flex_client.get_collection_items(collection_uuid)
        
        results = []
        for item in items:
            results.append({
                "id": item.id,
                "type": item.type,
                "name": item.item_name if hasattr(item, 'item_name') else None,
                "in_timecode": item.in_timecode if hasattr(item, 'in_timecode') else None,
                "out_timecode": item.out_timecode if hasattr(item, 'out_timecode') else None,
            })
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "count": len(results),
                "items": results
            }, indent=2)
        )]
    
    async def _get_workflows(self, arguments: dict) -> list[types.TextContent]:
        """Get list of workflow definitions"""
        filters = arguments.get("filters")
        
        workflows = self.flex_client.get_workflow_definitions(filters)
        
        results = []
        for workflow in workflows:
            results.append({
                "id": workflow.id,
                "uuid": workflow.uuid,
                "name": workflow.name,
                "displayName": workflow.display_name,
                "enabled": workflow.enabled,
                "description": workflow.description,
            })
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "count": len(results),
                "workflows": results
            }, indent=2)
        )]
    
    async def _get_job(self, arguments: dict) -> list[types.TextContent]:
        """Get details of a specific job"""
        job_id = arguments.get("job_id")
        
        job = self.flex_client.get_job(job_id)
        
        result = {
            "id": job.id,
            "status": job.status,
            "created": job.created if hasattr(job, 'created') else None,
            "progress": job.progress if hasattr(job, 'progress') else None,
            "error": job.error if hasattr(job, 'error') else None,
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    async def _get_asset_metadata(self, arguments: dict) -> list[types.TextContent]:
        """Get metadata for a specific asset"""
        asset_id = arguments.get("asset_id")
        
        metadata = self.flex_client.get_asset_metadata(asset_id)
        
        return [types.TextContent(
            type="text",
            text=json.dumps(metadata, indent=2)
        )]
    
    async def _get_users(self, arguments: dict) -> list[types.TextContent]:
        """Get list of users"""
        filters = arguments.get("filters")
        
        users = self.flex_client.get_users(filters)
        
        results = []
        for user in users:
            results.append({
                "id": user.id,
                "uuid": user.uuid,
                "name": user.name,
                "displayName": user.display_name,
                "email": user.email,
            })
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "count": len(results),
                "users": results
            }, indent=2)
        )]
    
    async def _get_asset_annotations(self, arguments: dict) -> list[types.TextContent]:
        """Get annotations for a specific asset"""
        asset_id = arguments.get("asset_id")
        limit = arguments.get("limit", 100)
        
        annotations = self.flex_client.get_annotations(asset_id)
        annotations = annotations[:limit]
        
        results = []
        for annotation in annotations:
            results.append({
                "id": annotation.id,
                "type": annotation.type if hasattr(annotation, 'type') else None,
                "timestamp_in": annotation.timestamp_in if hasattr(annotation, 'timestamp_in') else None,
                "timestamp_out": annotation.timestamp_out if hasattr(annotation, 'timestamp_out') else None,
                "text": annotation.text if hasattr(annotation, 'text') else None,
            })
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "count": len(results),
                "annotations": results
            }, indent=2)
        )]
    
    async def _search_assets_fql(self, arguments: dict) -> list[types.TextContent]:
        """Search for assets using FQL (Flex Query Language)"""
        query = arguments.get("query")
        limit = arguments.get("limit", 100)
        
        # Construct FQL filter
        fql_filter = f"fql={query}"
        
        try:
            assets = self.flex_client.get_assets(fql_filter, offset=0)
            assets = assets[:limit]
            
            results = []
            for asset in assets:
                results.append({
                    "id": asset.id,
                    "name": asset.name,
                    "title": asset.title,
                    "type": asset.type,
                    "status": asset.status,
                    "created": asset.created,
                })
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "count": len(results),
                    "query": query,
                    "assets": results
                }, indent=2)
            )]
        except Exception as e:
            # If FQL fails, provide helpful error message
            error_msg = str(e)
            if "401" in error_msg:
                help_text = "\n\nNote: FQL queries require proper syntax. Examples:\n" \
                           "- Simple text search: 'title:Olympics'\n" \
                           "- Phrase search: 'description:\"London 2012\"'\n" \
                           "- Field search: 'metadata.event:Olympics'\n" \
                           "- Combined: 'title:Olympics AND created > \"2024-01-01\"'"
                error_msg += help_text
            raise Exception(error_msg)
    
    async def _get_metadata_definition_fields(self, arguments: dict) -> list[types.TextContent]:
        """Get metadata definition fields"""
        metadata_definition_id = arguments.get("metadata_definition_id")
        
        try:
            fields_info = self.flex_client.get_metadata_definition_fields(metadata_definition_id)
            
            # Extract field information
            fields = []
            if isinstance(fields_info, dict) and 'fields' in fields_info:
                for field in fields_info.get('fields', []):
                    fields.append({
                        "name": field.get("name"),
                        "type": field.get("type"),
                        "label": field.get("label"),
                        "required": field.get("required", False)
                    })
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "metadataDefinitionId": metadata_definition_id,
                    "fields": fields,
                    "usage": f"To search by metadata, use: metadata=fieldname:value;metadataDefinitionId={metadata_definition_id}"
                }, indent=2)
            )]
        except Exception as e:
            error_msg = str(e)
            error_msg += "\n\nTo find metadata definition IDs, you may need to check asset metadata first using get_asset_metadata."
            raise Exception(error_msg)
    
    async def _search_objects(self, arguments: dict) -> list[types.TextContent]:
        """Search for any object type using the generic objects endpoint
        
        This method can search for:
        - Standard Flex objects (assets, collections, users, etc.) using object_type
        - User Defined Objects (UDOs) using plural_name
        """
        object_type = arguments.get("object_type", "")
        plural_name = arguments.get("plural_name", "")
        filters = arguments.get("filters", "")
        limit = arguments.get("limit", 100)
        include_data = arguments.get("include_data", False)
        
        # Validate that either object_type or plural_name is provided
        if not object_type and not plural_name:
            raise ValueError("Either 'object_type' or 'plural_name' must be provided")
        
        try:
            # Use the generic get_objects_by_filters method
            # If plural_name is provided, it takes precedence (for UDOs)
            if plural_name:
                # For UDOs, pass None as type and use plural_name parameter
                objects = self.flex_client.get_objects_by_filters(
                    type=None,
                    filters=filters,
                    limit=limit,
                    offset=0,
                    pagination=False,
                    plural_name=plural_name
                )
            else:
                # For standard objects, use the type parameter
                objects = self.flex_client.get_objects_by_filters(
                    type=object_type,
                    filters=filters,
                    limit=limit,
                    offset=0,
                    pagination=False
                )
            
            results = []
            for obj in objects[:limit]:
                obj_data = {
                    "id": obj.id if hasattr(obj, 'id') else None,
                    "uuid": obj.uuid if hasattr(obj, 'uuid') else None,
                    "name": obj.name if hasattr(obj, 'name') else None,
                    "type": obj.type if hasattr(obj, 'type') else None,
                    "created": obj.created if hasattr(obj, 'created') else None,
                }
                
                # Add any additional attributes that might exist
                if hasattr(obj, 'title'):
                    obj_data["title"] = obj.title
                if hasattr(obj, 'description'):
                    obj_data["description"] = obj.description
                if hasattr(obj, 'status'):
                    obj_data["status"] = obj.status
                    
                # Include full object data if requested
                if include_data and hasattr(obj, 'data'):
                    obj_data["data"] = obj.data
                    
                results.append(obj_data)
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "count": len(results),
                    "object_type": object_type or f"UDO: {plural_name}",
                    "filters": filters,
                    "objects": results
                }, indent=2)
            )]
            
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg and plural_name:
                error_msg += f"\n\nThe plural name '{plural_name}' was not found. "
                error_msg += "Make sure to use the exact plural name as defined in Flex for your UDO type."
            raise Exception(error_msg)
    
    async def _test_connection(self, arguments: dict) -> list[types.TextContent]:
        """Test the connection to Flex API"""
        result = {
            "status": "unknown",
            "flex_client_initialized": self.flex_client is not None,
            "environment_variables": {
                "FLEX_ENV_URL": os.getenv('FLEX_ENV_URL') is not None,
                "FLEX_ENV_USERNAME": os.getenv('FLEX_ENV_USERNAME') is not None,
                "FLEX_ENV_PASSWORD": os.getenv('FLEX_ENV_PASSWORD') is not None,
            },
            "current_directory": os.getcwd(),
            "env_file_exists": os.path.exists('.env'),
            "test_api_call": None,
            "error": None
        }
        
        if not self.flex_client:
            result["status"] = "not_initialized"
            result["error"] = "Flex client not initialized. Check environment variables."
        else:
            try:
                # Try a simple API call
                users = self.flex_client.get_users()
                result["status"] = "connected"
                result["test_api_call"] = f"Successfully retrieved {len(users)} users"
                result["api_url"] = os.getenv('FLEX_ENV_URL')
            except Exception as e:
                result["status"] = "auth_failed"
                result["error"] = str(e)
                result["api_url"] = os.getenv('FLEX_ENV_URL')
                
                if "401" in str(e):
                    result["error_details"] = "401 Unauthorized - Check username/password or API permissions"
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    async def initialize(self):
        """Initialize the Flex client with credentials from environment"""
        try:
            # Try to load from .env file first
            load_dotenv()
            
            base_url = os.getenv('FLEX_ENV_URL')
            username = os.getenv('FLEX_ENV_USERNAME')
            password = os.getenv('FLEX_ENV_PASSWORD')
            
            # Debug logging
            logger.info(f"Environment check - URL: {base_url is not None}, Username: {username is not None}, Password: {'*' * len(password) if password else None}")
            
            if not all([base_url, username, password]):
                logger.warning("Flex credentials not found in environment variables")
                logger.warning("Please set FLEX_ENV_URL, FLEX_ENV_USERNAME, and FLEX_ENV_PASSWORD")
                logger.warning(f"Current working directory: {os.getcwd()}")
                logger.warning(f"Looking for .env file at: {os.path.join(os.getcwd(), '.env')}")
                return
            
            logger.info(f"Initializing Flex client with URL: {base_url}")
            self.flex_client = FlexApiClient(base_url, username, password)
            logger.info("Flex client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Flex client: {str(e)}")
    
    async def run(self):
        """Run the MCP server"""
        await self.initialize()
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, 
                write_stream,
                InitializationOptions(
                    server_name="flex-mcp-server",
                    server_version="0.1.0",
                    capabilities={}
                )
            )

def main():
    """Main entry point"""
    server = FlexMCPServer()
    asyncio.run(server.run())

if __name__ == "__main__":
    main()