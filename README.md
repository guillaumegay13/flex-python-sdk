Clone this repo, then install the flex-python-sdk library using : 

```pip install -e {path-to-the-repo}```

You might need to update your PYTHONPATH :

```export PYTHONPATH="${PYTHONPATH}:{absolute-path-to-the-repo}"```

Example usage : 

```
import os
from flex.flex_api_client import FlexApiClient
from flex.flex_objects import Collection, Item

base_url = os.environ['FLEX_ENV_URL'] # for exemple, https://my-env.com/api
username = os.environ['FLEX_ENV_USERNAME']
password = os.environ['FLEX_ENV_PASSWORD']

# Get Collections
flex_api_client = FlexApiClient(base_url, username, password)
collections: list[Collection] = flex_api_client.get_collections()
for collection in collections:
    if collection.name == "Thematic Collections":
        thematic_collection = flex_api_client.get_collection(collection.uuid)
        print(f"Found {len(thematic_collection.sub_collections)} subCollections!")
        for sub_collection in thematic_collection.sub_collections:
            metadatas = flex_api_client.get_collection_metadata(sub_collection.uuid)["metadatas"][0]
            metadata_definition_entity_id = metadatas["metadataDefinitionEntityId"]
            metadata = metadatas["metadata"]
            metadata["publish-collection"] = "true"
            metadata_to_set = {"metadata": metadata}
            metadata_to_set["revision"] = metadatas["revision"]
            flex_api_client.update_collection_metadata(sub_collection.uuid, metadata_to_set, metadata_definition_entity_id)
