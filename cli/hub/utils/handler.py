import json
import os
import py7zr
from functools import cached_property
from ..settings import *
import requests
from .loader import Loader
from .api_requests import *
from .uuid import is_valid_uuid

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
        list_ = []
        page = api_get(f"{self.context.SPLIGHT_HUB_API_HOST}/{type}/", headers=headers)
        page = page.json()
        if page["results"]:
            list_.extend(page["results"])
        while page["next"] is not None:
            page = api_get(page["next"], headers=headers)
            page = page.json()
            if page["results"]:
                list_.extend(page["results"])
        return list_

    def exists_in_hub(self, type, name, version):
        headers = self.authorization_header
        response = api_get(f"{self.context.SPLIGHT_HUB_API_HOST}/{type}/mine/?name={name}&version={version}", headers=headers)
        response = response.json()

class DatalakeHandler:

    def __init__(self, context):
        self.context = context

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

    def list_source(self):
        list_ = []
        list_with_algo = []
        headers = self.authorization_header
        page = api_get(f"{self.context.SPLIGHT_PLATFORM_API_HOST}/datalake/source/", headers=headers) #TODO: check trailing slash
        page = page.json()
        if page["results"]:
            list_.extend(l['source'] for l in page["results"])
        while page["next"] is not None:
            page = api_get(page["next"], headers=headers)
            page = page.json()
            if page["results"]:
                list_.extend(l['source'] for l in page["results"])

        id_in_str = ""
        for source in list_:
            id_in_str += f"{source}," if is_valid_uuid(source) else ""
        if id_in_str[-1] == ',':
            id_in_str = id_in_str[:-1]

        algos = api_get(f"{self.context.SPLIGHT_PLATFORM_API_HOST}/algorithm/", params={'id__in': id_in_str}, headers=headers)
        for source in list_:
            filtered = list(filter(lambda algo: algo['id'] == source, algos.json()['results']))
            if filtered:
                list_with_algo.append({'source': source, 'algo': filtered[0].get('name')})
            else:
                list_with_algo.append({'source': source, 'algo': "-"})
        return list_with_algo
            

    def dump(self, source, path):
        headers = self.authorization_header
        file_data = api_get(f"{self.context.SPLIGHT_PLATFORM_API_HOST}/datalake/dumpdata/", params={'source': source}, headers=headers)
        with open(path, "wb+") as f:
            f.write(file_data.content)


    