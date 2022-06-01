import json
import os
import py7zr
from functools import cached_property
from ..settings import *
import requests
from .loader import Loader
from .api_requests import *

class ComponentHandler:

    def __init__(self, context):
        self.context = context

    @property
    def authorization_header(self):
        return {
            'Authorization': f"Splight {self.context.SPLIGHT_ACCESS_ID} {self.context.SPLIGHT_SECRET_KEY}"
        }

    def upload_component(self, type, name, version, parameters, local_path):
        """
        Save the component to the hub.
        """
        versioned_name = f"{name}-{version}"
        compressed_filename = f"{versioned_name}.{COMPRESSION_TYPE}"
        with Loader("Pushing component to Splight Hub..."):
            try:
                with py7zr.SevenZipFile(compressed_filename, 'w') as archive:
                    archive.writeall(local_path, versioned_name)
                headers = self.authorization_header
                data = {
                    'name': name,
                    'version': version,
                    'privacy_policy': self.context.privacy_policy.value,
                    'parameters': json.dumps(parameters),
                }
                files = {
                    'file': open(compressed_filename, 'rb'),
                    'readme': open(os.path.join(local_path, README_FILE), 'rb'),
                }
                response = api_post(f"{self.context.SPLIGHT_HUB_API_HOST}/{type}/upload/", files=files, data=data, headers=headers)

                if response.status_code != 201:
                    raise Exception(f"Failed to push component: {response.text}")
            except Exception as e:
                print(str(e))
            finally:
                if os.path.exists(compressed_filename):
                    os.remove(compressed_filename)

    def download_component(self, type, name, version, local_path):
        """
        Download the component from the hub.
        """
        with Loader("Pulling component from Splight Hub..."):
            headers = self.authorization_header
            data = {
                'name': name,
                'version': version,
            }
            response = api_post(f"{self.context.SPLIGHT_HUB_API_HOST}/{type}/download/", data=data, headers=headers)

            if response.status_code != 200:
                if response.status_code == 404:
                    raise Exception(f"Component not found")
                raise Exception(f"Failed to pull the component from splight hub")
                
            versioned_name = f"{name}-{version}"
            compressed_filename = f"{versioned_name}.{COMPRESSION_TYPE}"
            try:
                with open(compressed_filename, "wb") as f:
                    f.write(response.content)

                with py7zr.SevenZipFile(compressed_filename, "r") as z:
                    z.extractall(path=local_path)
            finally:
                if os.path.exists(compressed_filename):
                    os.remove(compressed_filename)

    def list_components(self, type):
        headers = self.authorization_header
        list = []
        page = api_get(f"{self.context.SPLIGHT_HUB_API_HOST}/{type}/", headers=headers)
        page = page.json()
        if page["results"]:
            list.extend(page["results"])
        while page["next"] is not None:
            page = api_get(page["next"], headers=headers)
            page = page.json()
            if page["results"]:
                list.extend(page["results"])
        return list

    def exists_in_hub(self, type, name, version):
        headers = self.authorization_header
        response = api_get(f"{self.context.SPLIGHT_HUB_API_HOST}/{type}/mine/?name={name}&version={version}", headers=headers)
        response = response.json()
        return response["count"] > 0

class DatalakeHandler:

    def __init__(self, context, client_class):
        self.context = context
        self.client = client_class(self.user_namespace)

    @property
    def authorization_header(self):
        return {
            'Authorization': f"Splight {self.context.SPLIGHT_ACCESS_ID} {self.context.SPLIGHT_SECRET_KEY}"
        }
    
    @cached_property
    def user_namespace(self):
        headers = self.authorization_header
        response = api_get(f"{self.context.SPLIGHT_PLATFORM_API_HOST}/admin/me", headers=headers)
        response = response.json()
        return response["organization_id"]

    def list_source(self, type):
        headers = self.authorization_header
        list = []
        page = api_get(f"{self.context.SPLIGHT_PLATFORM_API_HOST}/{type}/source/", headers=headers)
        page = page.json()
        if page["results"]:
            list.extend(l['source'] for l in page["results"])
        while page["next"] is not None:
            page = api_get(page["next"], headers=headers)
            page = page.json()
            if page["results"]:
                list.extend(l['source'] for l in page["results"])
        return list

    def dump(self):
        return self.client.list_collection_names()


    