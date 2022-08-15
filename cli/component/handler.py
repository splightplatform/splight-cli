# THIS CLASS SHOULD NOT EXISTS
# TODO MOVE THIS TO HUBCLIENT REMOTE_LIB IMPLEMENTATION 
import json
import os
import py7zr
from functools import cached_property
from cli.constants import *
from cli.context import PrivacyPolicy
from cli.utils.loader import Loader
from cli.utils.api_requests import *
from splight_lib import logging

logger = logging.getLogger()


class UserHandler:

    def __init__(self, context):
        self.context = context
        self.access_id = self.context.workspace.settings.SPLIGHT_ACCESS_ID
        self.secret_key = self.context.workspace.settings.SPLIGHT_SECRET_KEY
        self.host = self.context.workspace.settings.SPLIGHT_HUB_API_HOST

    @property
    def authorization_header(self):
        return {
            'Authorization': f"Splight {self.access_id} {self.secret_key}"
        }

    @cached_property
    def user_namespace(self):
        org_id = 'default'
        try:
            headers = self.authorization_header
            response = api_get(f"{self.context.SPLIGHT_PLATFORM_API_HOST}/admin/me", headers=headers)
            response = response.json()
            org_id = response.get("organization_id")
        except Exception:
            logger.warning("Could not check org_id remotely using default namespace")
        return org_id


class ComponentHandler:

    def __init__(self, context):
        self.context = context
        self.user_handler = UserHandler(context)

    def upload_component(self, type, name, version, parameters, public, local_path):
        """
        Save the component to the hub.
        """
        versioned_name = f"{name}-{version}"
        compressed_filename = f"{versioned_name}.{COMPRESSION_TYPE}"
        with Loader("Pushing component to Splight Hub..."):
            try:
                with py7zr.SevenZipFile(compressed_filename, 'w') as archive:
                    archive.writeall(local_path, versioned_name)
                headers = self.user_handler.authorization_header
                data = {
                    'name': name,
                    'version': version,
                    'privacy_policy': PrivacyPolicy.PUBLIC.value if public else PrivacyPolicy.PRIVATE.value,
                    'parameters': json.dumps(parameters),
                }
                files = {
                    'file': open(compressed_filename, 'rb'),
                    'readme': open(os.path.join(local_path, README_FILE), 'rb'),
                    'picture': open(os.path.join(local_path, PICTURE_FILE), 'rb'),
                }
                response = api_post(f"{self.user_handler.host}/{type}/upload/", files=files, data=data, headers=headers)
                if response.status_code != 201:
                    raise Exception(f"Failed to push component: {response.text}")
            except Exception as e:
                raise e
            finally:
                if os.path.exists(compressed_filename):
                    os.remove(compressed_filename)
                
    def download_component(self, type, name, version, local_path):
        """
        Download the component from the hub.
        """
        with Loader("Pulling component from Splight Hub..."):
            headers = self.user_handler.authorization_header
            data = {
                'name': name,
                'version': version,
            }
            response = api_post(f"{self.user_handler.host}/{type}/download/", data=data, headers=headers)

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

    def delete_component(self, type, name, version):
        """
        Download the component from the hub.
        """
        with Loader("Deleting component from Splight Hub..."):
            headers = self.user_handler.authorization_header
            data = {
                'name': name,
                'version': version,
            }
            response = api_post(f"{self.user_handler.host}/{type}/remove/", data=data, headers=headers)

            if response.status_code != 201:
                if response.status_code == 404:
                    raise Exception(f"Component not found")
                raise Exception(f"Failed to delete the component from splight hub")

    def list_components(self, type):
        headers = self.user_handler.authorization_header
        list_ = []
        page = api_get(f"{self.user_handler.host}/{type}/", headers=headers)
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
        headers = self.user_handler.authorization_header
        response = api_get(f"{self.user_handler.host}/{type}/mine/?name={name}&version={version}", headers=headers)
        response = response.json()
        return response["count"] > 0
