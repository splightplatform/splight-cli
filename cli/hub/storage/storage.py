import boto3
import json
import os
import py7zr

from ..settings import (
    README_FILE,
    SPEC_FILE,
)

from .settings import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    AWS_STORAGE_HUB_BUCKET_NAME,
)
class S3HubClient:

    def __init__(self):
        self.s3_client = self._get_s3_client()
        self.s3_resource = self._get_s3_resource()

    def _get_s3_client(self):
        return boto3.client("s3",
                            aws_access_key_id=AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                            region_name=AWS_REGION)

    def _get_s3_resource(self):
        return boto3.resource("s3",
                            aws_access_key_id=AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                            region_name=AWS_REGION)


    def save_component_raw(self, type, versioned_name, local_path):
        """
        Save a component to the hub.
        Originally used to save folder to hub in versions from 0.0.0 - 0.0.7
        """
        for (dirpath, _, filenames) in os.walk(local_path):
            hub_directory_path = versioned_name + dirpath.replace(local_path, "")
            for filename in filenames:
                local_file = os.path.join(dirpath, filename)
                key = type + "/" + hub_directory_path + "/" + filename
                self.save_file(local_file, key)


    def save_component(self, type, versioned_name, local_path):
        """
        Save the component to the hub.
        Saves 7z file + README + spec.json in path: type/versioned_name
        """
        self._save_component_data(type, versioned_name, local_path)
        self._save_component_zip(type, versioned_name, local_path)


    def _save_component_data(self, type, versioned_name, local_path):
        """
        Saves README + spec.json in path: type/versioned_name
        """
        for filename in [SPEC_FILE, README_FILE]:
            key = type + "/" + versioned_name + "/" + filename

            if filename == SPEC_FILE:
                spec = {}
                with open(os.path.join(local_path, filename), "r") as f:
                    spec = json.load(f)

                spec["readme"] = f"https://{AWS_STORAGE_HUB_BUCKET_NAME}.s3.amazonaws.com/{type}/{versioned_name}/{README_FILE}"
            
                with open(os.path.join(local_path, filename), "w") as f:
                    f.write(json.dumps(spec, indent=4))

                self.save_file(os.path.join(local_path, filename), key)
                spec.pop("readme")

                with open(os.path.join(local_path, filename), "w") as f:
                    f.write(json.dumps(spec, indent=4))
                
            else:
                self.save_file(os.path.join(local_path, filename), key)


    def _save_component_zip(self, type, versioned_name, local_path):
        """
        Saves 7z file in path: type/versioned_name
        """
        sevenz_filename = f"{versioned_name}.7z"
        try:
            with py7zr.SevenZipFile(sevenz_filename, 'w') as archive:
                archive.writeall(local_path, versioned_name)
            self.save_file(sevenz_filename, f"{type}/{versioned_name}/{sevenz_filename}")
        finally:
            if os.path.exists(sevenz_filename):
                os.remove(sevenz_filename)


    def save_file(self, local_file, key) -> None:
        """
        Save a file to the hub.
        """
        self.s3_client.upload_file(
            Filename=local_file,
            Bucket=AWS_STORAGE_HUB_BUCKET_NAME,
            Key=key
        )


    def list_components(self, type, spec_file_name):
        """
        List all components of a given type.
        """
        files = self.s3_client.list_objects(
            Bucket=AWS_STORAGE_HUB_BUCKET_NAME,
            Prefix=type
        ).get('Contents', [])

        components = set()
        result = []
        for obj in files:
            key = obj['Key']
            key = key.replace(f"{type}/", "")
            component = key.split("/")[0]
            if component not in components:
                components.add(component)
                spec_key = f"{type}/{component}/{spec_file_name}"
                obj = self.s3_resource.Object(AWS_STORAGE_HUB_BUCKET_NAME, spec_key)
                spec = json.loads(obj.get()['Body'].read().decode('utf-8'))
                result.append(spec)
        return result


    def download_dir_raw(self, dir_name, dist, local_path="/tmp", bucket=AWS_STORAGE_HUB_BUCKET_NAME):
        """
        Download a directory from the hub. Raw version
        """
        paginator = self.s3_client.get_paginator("list_objects")
        for result in paginator.paginate(Bucket=bucket, Delimiter="/", Prefix=dist):
            if result.get("CommonPrefixes") is not None:
                for subdir in result.get("CommonPrefixes"):
                    self.download_dir_raw(dir_name, subdir.get("Prefix"), local_path, bucket)
            for file in result.get("Contents", []):
                dest_pathname = os.path.join(local_path, file.get("Key")).split("/")
                while dest_pathname[0] != dir_name:
                    dest_pathname.pop(0)
                dest_pathname = str.join("/", dest_pathname)
                if not os.path.exists(os.path.dirname(dest_pathname)):
                    os.makedirs(os.path.dirname(dest_pathname))
                if not file.get("Key").endswith("/"):
                    self.s3_resource.meta.client.download_file(bucket, file.get("Key"), dest_pathname)


    def download_dir(self, type, versioned_name, local_path="/tmp"):
        """
        Download a directory from the hub. Zip version
        """
        sevenz_filename = f"{versioned_name}.7z"
        self.s3_resource.meta.client.download_file(AWS_STORAGE_HUB_BUCKET_NAME, f"{type}/{versioned_name}/{sevenz_filename}", sevenz_filename)
        try:
            with py7zr.SevenZipFile(sevenz_filename, 'r') as z:
                z.extractall(path=local_path)
        finally:
            os.remove(sevenz_filename)


    def exists_in_hub(self, type, name) -> bool:
        """
        Check if a component exists in the hub.
        """
        return len(self.s3_client.list_objects(
            Bucket=AWS_STORAGE_HUB_BUCKET_NAME,
            Prefix=f"{type}/{name}"
        ).get('Contents', [])) > 0