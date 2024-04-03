import requests
import base64
import datetime
from objects.flex_objects import FlexInstance, FlexAsset
from datetime import datetime, timedelta
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from flex_objects import Action

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
        """Get actions."""
        if filters:
            endpoint = f"/actions;{filters}"
        else:
            endpoint = f"/actions"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            action_list = [Action(action) for action in response.json().get('actions', [])]
            return action_list
        except requests.RequestException as e:
            raise Exception(e)
    
    def get_action(self, actionId):
        """Get action."""
        endpoint = f"/actions/{actionId}"
        try:
            response = requests.get(self.base_url + endpoint, headers=self.headers)
            response.raise_for_status()
            action = Action(response.json())
            return action
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
            
            response = requests.post(self.base_url + endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            action = Action(response.json())
            return action
        except requests.RequestException as e:
            raise Exception(e)