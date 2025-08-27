# Flex Python SDK

A Python client library for interacting with the Dalet Flex API.

## Installation

```bash
pip install flex-sdk
```

For development mode:
```bash
# Clone the repository
git clone <repository-url>
cd flex-python-sdk

# Install in development mode
pip install -e .

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

```python
import os
from flex.flex_api_client import FlexApiClient
from flex.flex_objects import Collection, Item

# Set up authentication using environment variables
base_url = os.environ['FLEX_ENV_URL']  # e.g., https://my-env.com/api
username = os.environ['FLEX_ENV_USERNAME']
password = os.environ['FLEX_ENV_PASSWORD']

# Create client
flex_api_client = FlexApiClient(base_url, username, password)

# Get assets
assets = flex_api_client.get_assets()
for asset in assets:
    print(f"Asset: {asset.name} (ID: {asset.id})")
```

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

### Key Features

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

## Common Use Cases

### Asset Operations

```python
# Get assets with filters
assets = flex_api_client.get_assets(filters={"status": "active"})

# Get assets with parallel fetching for better performance
assets = flex_api_client.get_assets_parallel(filters={"status": "active"})

# Update asset metadata
flex_api_client.set_asset_metadata(asset_id, {"title": "New Title", "description": "Updated description"})

# Get asset annotations
annotations = flex_api_client.get_annotations(asset_id)

# Add keyframe
flex_api_client.create_keyframe(asset_id, timestamp=1000, image_data=base64_encoded_image)
```

### Job Management

```python
# Create a job
job = flex_api_client.create_job({
    'assetId': asset_id, 
    'actionId': action_id
})

# Monitor job status
job_status = flex_api_client.get_job(job.id)
print(f"Job status: {job_status.status}")

# Get job history
history = flex_api_client.get_job_history(job.id)

# Retry failed job
if job_status.status == "failed":
    new_job = flex_api_client.retry_job(job.id)
```

### Collection Management

```python
# Create collection
collection = flex_api_client.create_collection({
    "name": "My Collection",
    "description": "Collection description"
})

# Add items to collection
flex_api_client.add_item_to_collection(collection.id, asset_id)

# Get collection items
items = flex_api_client.get_collection_items(collection.id)

# Update collection
flex_api_client.update_collection(collection.id, {"name": "Updated Name"})
```

### Taxonomy Operations

```python
# Create taxonomy
taxonomy = flex_api_client.create_taxonomy({
    "name": "Genre",
    "description": "Media genres"
})

# Add taxons (categories)
taxon = flex_api_client.create_taxon(taxonomy.id, {
    "name": "Documentary",
    "parent_id": None  # Top-level taxon
})

# Create sub-taxon
sub_taxon = flex_api_client.create_taxon(taxonomy.id, {
    "name": "Nature Documentary",
    "parent_id": taxon.id
})
```

## Example Scripts

### Parse a CSV of asset IDs and launch a job on each asset

```python
from flex.flex_api_client import FlexApiClient
import csv

flex_api_client = FlexApiClient(base_url, username, password)

with open('assets_to_fix.csv', 'r') as file:
    reader = csv.reader(file)
    header = next(reader)

    for row in reader:
        asset_id = row[0]
        job = flex_api_client.create_job({'assetId': asset_id, 'actionId': action_id})   
        print(f'Launched job id {job.id} on asset id {asset_id}')
```

### Delete annotations with 00:00:00:00 duration from an asset

```python
from flex.flex_api_client import FlexApiClient
from flex.flex_objects import Annotation

flex_api_client = FlexApiClient(base_url, username, password)

asset_id = 'your-asset-id'

annotations = flex_api_client.get_annotations(asset_id)

for annotation in annotations:
    if annotation.timestamp_in == annotation.timestamp_out:
        flex_api_client.delete_annotation(annotation.id)
```

### Advanced Examples

Find more complex examples in the examples repository, such as [this script](examples/extract_assets_with_wrong_keyframes.py).

## Important Notes

- The SDK increases Python's recursion limit to 1500 for deep pagination
- All timestamps are in microseconds
- Content-Type header is set to `application/vnd.nativ.mio.v1+json`
- The SDK is designed for Dalet Flex version that uses this API format

## Building and Distribution

```bash
# Build the package
python -m build

# Upload to PyPI (requires authentication)
python -m twine upload dist/*
```

## Contributing

Feel free to contribute and add your script examples. Please make sure to **always remove environment related information**.

## License

See LICENSE file for details.