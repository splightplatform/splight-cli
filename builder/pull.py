import boto3

# import tarfile
import py7zr


def porfavor_get_path(hub_component_id, name, version):
    return f"component_files/{hub_component_id}/{name}-{version}.7z"


def porfavor_get_file_name(name, version):
    return f"{name}-{version}.tgz".lower()


def holaa():
    return "see.7z"


def porfavor_download_zip_component(hub_component_id, name, version):
    print("See")
    s3_client = boto3.client("s3")
    s3_client.download_file(
        Bucket="integration-splight-api-storage",
        Key="component_files/97f71a89-b42e-4ecb-b02a-51965d974d44/Sum-1.1.5.7z",
        Filename=holaa(),
    )
    # return 0


def porfavor_uncompress(name, version):
    with py7zr.SevenZipFile(holaa(), "r") as z:
        z.extractall(path=".")
