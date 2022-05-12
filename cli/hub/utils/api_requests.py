import requests
import json
from ..settings import *

def authentication_api_validation(response):
    if response.status_code not in [200, 201]:
        response = response.json()
        detail = response.get("detail", None)
        if detail == "Invalid token.":
            raise Exception(f"Invalid token. Please check your SPLIGHT_HUB_TOKEN environment variable.")
        if detail == "Authentication credentials were not provided.":
            raise Exception(f"Authentication credentials were not provided. Please check your SPLIGHT_HUB_TOKEN environment variable.")
        raise Exception(f"An unknown error ocurred while trying to reach Splight Hub API: {json.dumps(response)}")
    return response

def hub_api_get(*args, **kwargs):
    response = requests.get(*args, **kwargs)
    response = authentication_api_validation(response)
    return response

def hub_api_post(*args, **kwargs):
    response = requests.post(*args, **kwargs)
    response = authentication_api_validation(response)
    return response


    