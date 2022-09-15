import requests
import json
from functools import wraps
from cli.constants import *
from requests.exceptions import ConnectionError

def http_request_validation(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            response = func(*args, **kwargs)
            if response.status_code >= 400:
                response = response.json()
                detail = response.get("detail", None)

                if detail in ["Invalid token.", "Authentication credentials were not provided.", "Incorrect authentication credentials."]:
                    raise Exception(f"{detail} Please check your Splight credentials. Use 'splightcli configure'")

                raise Exception(f"An unknown error ocurred while trying to reach Splight Hub API: {json.dumps(response)}")
            return response
        except ConnectionError:
            raise Exception(f"Splight Hub API is unreachable: Check out your configuration for Splight Hub API host. Use 'splightcli configure'")
    return wrapper

@http_request_validation
def api_get(*args, **kwargs):
    return requests.get(*args, **kwargs)

@http_request_validation
def api_post(*args, **kwargs):
    return requests.post(*args, **kwargs)

@http_request_validation
def api_delete(*args, **kwargs):
    return requests.delete(*args, **kwargs)
