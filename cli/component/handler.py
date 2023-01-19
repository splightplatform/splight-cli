# THIS CLASS SHOULD NOT EXISTS
# TODO MOVE THIS TO HUBCLIENT REMOTE_LIB IMPLEMENTATION
import os
import py7zr
import shutil
from typing import Dict, Optional
from functools import cached_property
from cli.constants import *
from cli.utils.loader import Loader
from cli.utils.api_requests import *
from cli.component.spec import Spec, PrivacyPolicy
from splight_lib import logging

logger = logging.getLogger()


class UserHandler:

    def __init__(self, context):
        self.context = context
        self.access_id = self.context.workspace.settings.SPLIGHT_ACCESS_ID
        self.secret_key = self.context.workspace.settings.SPLIGHT_SECRET_KEY
        self.host = self.context.workspace.settings.SPLIGHT_PLATFORM_API_HOST

    @property
    def authorization_header(self):
        return {
            'Authorization': f"Splight {self.access_id} {self.secret_key}"
        }

    @cached_property
    def user_namespace(self):
        org_id = DEFAULT_NAMESPACE
        try:
            headers = self.authorization_header
            response = api_get(f"{self.host}/admin/me", headers=headers)
            response = response.json()
            org_id = response.get("organization_id")
        except Exception:
            logger.warning("Could not check org_id remotely using default namespace")
        return org_id


class ComponentHandler:

    def __init__(self, context):
        self.context = context
        self.user_handler = UserHandler(context)

    def upload_component(self, spec: Spec, local_path):
        versioned_name = f"{spec.name}-{spec.version}"
        compressed_filename = f"{versioned_name}.{COMPRESSION_TYPE}"
        with Loader("Pushing component to Splight Hub..."):
            try:
                with py7zr.SevenZipFile(compressed_filename, 'w') as archive:
                    archive.writeall(local_path, versioned_name)
                headers = self.user_handler.authorization_header
                data = {
                    'name': spec.name,
                    'version': spec.version,
                    'splight_cli_version': spec.splight_cli_version,
                    'privacy_policy': spec.privacy_policy.value if isinstance(spec.privacy_policy, PrivacyPolicy) else spec.privacy_policy,
                    'tags': spec.tags,
                    'custom_types': json.dumps([x.dict() for x in spec.custom_types]),
                    'input': json.dumps([x.dict() for x in spec.input]),
                    'output': json.dumps([x.dict() for x in spec.output]),
                    'commands': json.dumps([x.dict() for x in spec.commands]),
                    'bindings': json.dumps([x.dict() for x in spec.bindings]),
                    'endpoints': json.dumps([x.dict() for x in spec.endpoints]),
                }
                files = {
                    'file': open(compressed_filename, 'rb'),
                    'readme': open(
                        os.path.join(local_path, README_FILE), 'rb'
                    )
                }
                response = api_post(
                    f"{self.user_handler.host}/hub/upload/",
                    files=files,
                    data=data,
                    headers=headers
                )
                if response.status_code != 201:
                    raise Exception(f"Failed to push component: {response.text}")
            except Exception as e:
                raise e
            finally:
                if os.path.exists(compressed_filename):
                    os.remove(compressed_filename)

    def download_component(self, name, version):
        with Loader("Pulling component from Splight Hub..."):
            headers = self.user_handler.authorization_header
            data = {
                'name': name,
                'version': version,
            }
            response = api_post(
                f"{self.user_handler.host}/hub/download/",
                data=data,
                headers=headers
            )

            if response.status_code != 200:
                if response.status_code == 404:
                    raise Exception("Component not found")
                raise Exception("Failed to pull the component from splight hub")

            versioned_name = f"{name}-{version}"
            compressed_filename = f"{versioned_name}.{COMPRESSION_TYPE}"

            component_path = f"{name}/{version}"
            if os.path.exists(component_path):
                shutil.rmtree(component_path)
            try:
                with open(compressed_filename, "wb") as f:
                    f.write(response.content)

                with py7zr.SevenZipFile(compressed_filename, "r") as z:
                    z.extractall(path='.')
                shutil.move(f"{versioned_name}", component_path)
            finally:
                if os.path.exists(compressed_filename):
                    os.remove(compressed_filename)

    def delete_component(self, name, version):
        with Loader("Deleting component from Splight Hub..."):
            headers = self.user_handler.authorization_header
            response = api_get(
                f"{self.user_handler.host}/hub/mine/component-versions/?name={name}&version={version}",
                headers=headers
            )
            response = response.json()
            for item in response["results"]:
                response = api_delete(
                    f"{self.user_handler.host}/hub/mine/component-versions/{item['id']}/",
                    headers=headers
                )
                if response.status_code != 204:
                    raise Exception(
                        "Failed to delete the component from splight hub"
                    )

    def list_components(self):
        with Loader("Listing components.."):
            headers = self.user_handler.authorization_header
            list_ = []
            page = api_get(
                f"{self.user_handler.host}/hub/mine/components/",
                headers=headers
            )
            page = page.json()
            if page["results"]:
                list_.extend(page["results"])
            while page["next"] is not None:
                page = api_get(page["next"], headers=headers)
                page = page.json()
                if page["results"]:
                    list_.extend(page["results"])
        return list_

    def list_component_versions(self, name):
        with Loader("Listing component versions.."):
            headers = self.user_handler.authorization_header
            list_ = []
            page = api_get(
                f"{self.user_handler.host}/hub/mine/component-versions/?name={name}",
                headers=headers
            )
            page = page.json()
            if page["results"]:
                list_.extend(page["results"])
            while page["next"] is not None:
                page = api_get(page["next"], headers=headers)
                page = page.json()
                if page["results"]:
                    list_.extend(page["results"])
        return list_

    def exists_in_hub(self, name, version):
        headers = self.user_handler.authorization_header
        endpoints = [
            f"{self.user_handler.host}/hub/private/component-versions/?name={name}&version={version}"
            f"{self.user_handler.host}/hub/public/component-versions/?name={name}&version={version}"
        ]
        for endpoint in endpoints:
            response = api_get(endpoint, headers=headers)
            response = response.json()
            if response["count"] > 0:
                break
        return response["count"] > 0

    def create_component(
        self,
        component_name: str,
        component_version: str,
    ) -> Dict:
        endpoint = f"{self.user_handler.host}/"
        headers = self.user_handler.authorization_header
        data = {
            "name": f"CLI: {component_name}",
            "description": "created by Splight CLI",
            "version": component_version,
            "custom_types": [],
            "input": [],
            "output": [],
        }
        response = api_post(endpoint, headers=headers, data=data)
        response.raise_for_status()
        return response.json()

    def get_component_info(
        self,
        component_name: str,
        component_version: str
    ) -> Optional[Dict]:
        endpoint = f"{self.user_handler.host}/hub/all/component-versions/"
        headers = self.user_handler.authorization_header
        params = {
            "name": component_name,
            "version": component_version,
        }
        response = api_get(
            endpoint,
            headers=headers,
            params=params,
        )
        response.raise_for_status()
        component_list = response.json()["results"]
        component = component_list[0] if component_list else None
        return component
