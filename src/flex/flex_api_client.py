import requests
import base64
import datetime
from datetime import datetime, timedelta
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from flex.flex_objects import Action, WorkflowDefinition, User, Collection, Item, Asset, Workflow, Job

# Increase default recursion limit (from 999 to 1500)
# See : https://stackoverflow.com/questions/14222416/recursion-in-python-runtimeerror-maximum-recursion-depth-exceeded-while-callin
# max_number_of_objects_to_retrieve = limit * recursion_limit
sys.setrecursionlimit(1500)

class FlexApiClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        
        # Prepare basic authentication header
        credentials = f"{username}:{password}"
        base64_encoded_credentials = base64.b64encode(credentials.encode())
        auth_header = {'Authorization': f'Basic {base64_encoded_credentials.decode()}'}

        # Set Content-Type header and combine with additional headers
        self.headers = {
            'Content-Type': 'application/vnd.nativ.mio.v1+json',
            **auth_header,
        }
    
    def get_actions(self, filters = None):
        """Get Actions."""
        endpoint = f"/actions"
        if filters:
            endpoint += f";{filters}"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            action_list = [Action(action) for action in response.json().get('actions', [])]
            return action_list
        except requests.RequestException as e:
            raise Exception(e)
    
    def get_action(self, actionId):
        """Get Action."""
        endpoint = f"/actions/{actionId}"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            action = Action(response.json())
            return action
        except requests.RequestException as e:
            raise Exception(e)
        
    def get_workflow_definition(self, workflowDefinitionId):
        """Get Workflow Definition."""
        endpoint = f"/workflowDefinitions/{workflowDefinitionId}"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            workflow_definition = WorkflowDefinition(response.json())
            return workflow_definition
        except requests.RequestException as e:
            raise Exception(e)
        
    def get_workflow_definitions(self, filters = None):
        """Get Workflow Definitions."""
        endpoint = f"/workflowDefinitions"
        if filters:
            endpoint += f";{filters}"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            workflow_definition_list = [WorkflowDefinition(action) for action in response.json().get('workflowDefinitions', [])]
            return workflow_definition_list
        except requests.RequestException as e:
            raise Exception(e)
        
    def get_user(self, userId):
        """Get User."""
        endpoint = f"/users/{userId}"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            user = User(response.json())
            return user
        except requests.RequestException as e:
            raise Exception(e)
        
    def get_users(self, filters = None):
        """Get Users."""
        endpoint = f"/users"
        if filters:
            endpoint += f";{filters}"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            user_list = [User(action) for action in response.json().get('users', [])]
            return user_list
        except requests.RequestException as e:
            raise Exception(e)
        
    def create_action(self, name, type, pluginClass, pluginUuid, visibilityIds, additional_param):
        """Create a new action."""
        # Mandatory fields : name, type, pluginClass, visibilityIds
        endpoint = "/actions"
        try:
            payload = {
                        'name': name,
                        'type': type,
                        'pluginClass': pluginClass,
                        'pluginUuid': pluginUuid,
                        'visibilityIds': visibilityIds
                      }
            
            for param_name, param_value in additional_param.items():
                payload[param_name] = param_value
            
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            action = Action(response.json())
            return action
        except requests.RequestException as e:
            raise Exception(e)
        
    def create_workflow(self, payload):
        endpoint = f"/workflows"
        try:
            response = requests.post(self.base_url + endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            json_response = response.json()
            return Workflow(response.json())
        except requests.RequestException as e:
            raise Exception(e)
    
    def get_collections(self, filters = None) -> list[Collection]:
        """Get Collections."""
        endpoint = f"/collections"
        if filters:
            endpoint += f";{filters}"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            collection_list = [Collection(collection) for collection in response.json().get('collections', [])]
            return collection_list
        except requests.RequestException as e:
            raise Exception(e)
        
    def get_collection(self, collection_uuid) -> Collection:
        """Get Collections."""
        endpoint = f"/collections/{collection_uuid}"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            collection = Collection(response.json())
            return collection
        except requests.RequestException as e:
            raise Exception(e)
        
    def get_collection_items(self, collection_uuid, offset=0) -> list[Item]:
        """Get Collections Items."""
        limit = 100
        endpoint = f"/collections/{collection_uuid}/items?limit={limit}&offset={offset}"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            item_list = [Item(item) for item in response.json()["items"]]
            total_results = response.json()['totalResults']
            if (total_results > limit + offset):
                item_list.extend(self.get_collection_items(collection_uuid, offset + limit))

            return item_list
        except requests.RequestException as e:
            raise Exception(e)
        
    def update_collection_items(self, collection_uuid, item_list):
        """Update Collections Items."""
        endpoint = f"/collections/{collection_uuid}/items"
        try:
            items = []
            for item in item_list:
                item_json = {"id": item.id, "type": item.type}
                if (item.in_timecode):
                    item_json["in"] = item.in_timecode
                if (item.out_timecode):
                    item_json["out"] = item.out_timecode
                if (item.item_name):
                    item_json["itemName"] = item.item_name
                items.append(item_json)
            payload = {"items": items}
            print(payload)
            response = requests.put(self.base_url + endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(e)
        
    def delete_items_from_collection(self, collection_uuid, item_list):
        """Delete Items from Collection."""
        endpoint = f"/collections/{collection_uuid}/items"
        try:
            items_to_delete = []
            for item in item_list:
                items_to_delete.append(str(item.item_key))
            payload = {"itemKeys": items_to_delete}
            response = requests.delete(self.base_url + endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(e)
        
    def get_collection_metadata(self, collection_uuid, ):
        """Get Collection Metadata."""
        endpoint = f"/collections/{collection_uuid}/metadata"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(e)
        
    def update_collection_metadata(self, collection_uuid, metadata, metadata_definition_entity_id):
        """Update Collection Metadata."""
        endpoint = f"/collections/{collection_uuid}/metadata/{metadata_definition_entity_id}"
        try:
            response = requests.put(self.base_url + endpoint, json=metadata, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(e)
        
    def get_asset(self, asset_id):
        endpoint = f"/assets/{asset_id}"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            asset = Asset(response.json())
            return asset
        except requests.RequestException as e:
            raise Exception(e)

    def get_asset_workflows(self, asset_id):
        endpoint = f"/assets/{asset_id}/workflows"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            asset = [Workflow(workflow) for workflow in response.json()["workflows"]]
            return asset
        except requests.RequestException as e:
            raise Exception(e)
        
    def get_asset_metadata(self, asset_id):
        endpoint = f"/assets/{asset_id}/metadata"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()["instance"]
        except requests.RequestException as e:
            raise Exception(e)
        
    def set_asset_metadata(self, asset_id, metadata):
        endpoint = f"/assets/{asset_id}/metadata"
        try:
            response = requests.put(self.base_url + endpoint, json=metadata, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(e)
        
    def get_assets(self, filters, offset = 0):
        limit = 100
        endpoint = f"/assets;offset={offset};limit={100}"
        if filters:
            endpoint += f";{filters}"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            response_json = response.json()
            asset_list = [Asset(asset) for asset in response_json["assets"]]
            total_results = response_json["totalCount"]
            if (total_results > offset + limit):
                asset_list.extend(self.get_assets(filters, offset + limit))
            return asset_list
        except requests.RequestException as e:
            raise Exception(e)
        
    def delete_annotations(self, asset_id, originator_context, originator_correlation_id):
        endpoint = f"/assets/{asset_id}/annotations"
        try:
            payload = {
                        'originatorContext': originator_context,
                        'originatorCorrelationId': originator_correlation_id
                      }
            response = requests.delete(self.base_url + endpoint, json=payload,headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(e)
        
    def get_workflow_instance(self, workflow_id, include_variables = "false"):
        endpoint = f"/workflows/{workflow_id};includeVariables={include_variables}"
        try:
            response = requests.get(self.base_url + endpoint,headers=self.headers)
            response.raise_for_status()
            workflow = Workflow(response.json())
            return workflow
        except requests.RequestException as e:
            raise Exception(e)
        
    def get_job(self, job_id):
        endpoint = f"/jobs/{job_id}"
        try:
            response = requests.get(self.base_url + endpoint,headers=self.headers)
            response.raise_for_status()
            job = Job(response.json())
            return job
        except requests.RequestException as e:
            raise Exception(e)

    def cancel_job(self, job_id):
        """Cancel a job."""
        endpoint = f"/jobs/{job_id}/actions"
        try:
            job = self.get_job(job_id)
            job_status = job.status

            if job_status != "Failed":
                print(f"Couldn't cancel the job as it is not Failed, its status is : {job_status}")
                return job
            else:
                payload = {
                        'action': 'cancel'
                    }
                response = requests.post(self.base_url + endpoint, json=payload, headers=self.headers)
                response.raise_for_status()
                job = Job(response.json())
                print(f'Job ID {job_id} has been cancelled!')
                return job
        except requests.RequestException as e:
            print(f"POST request error: {e}")
            return None
        
    def get_workflow(self, workflow_id):
        """Get a workflow."""
        endpoint = f"/workflows/{workflow_id}"
        try:
                
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            workflow = Workflow(response.json())
            return workflow
        except requests.RequestException as e:
            raise Exception(e)

    def cancel_workflow(self, workflow_id):
        """Cancel a workflow."""
        endpoint = f"/workflows/{workflow_id}/actions"
        try:
            workflow = self.get_workflow(workflow_id)
            status = workflow.status

            if status != "Failed":
                print(f"Couldn't cancel the workflow ID {workflow_id} as it is not Failed, its status is : {status}")
                return workflow
            else:
                payload = {
                            'action': 'cancel'
                        }
                    
                response = requests.post(self.base_url + endpoint, json=payload, headers=self.headers)
                response.raise_for_status()
                workflow = Workflow(response.json())
                print(f'Workflow ID {workflow_id} has been cancelled!')
                return workflow
        except requests.RequestException as e:
            print(f"POST request error: {e}")
            return None