import requests
import json
from functools import wraps
from requests.exceptions import ConnectionError
import logging
from ..settings import *

logger = logging.getLogger()

def http_connection(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ConnectionError as e:
            logger.debug(f"{str(e)}")
            raise Exception(f"Splight Hub API is unreachable: Check out your configuration for Splight Hub API host. Use 'splighthub configure'")
    return wrapper


def authentication_api_validation(response):
    if response.status_code not in [200, 201]:
        response = response.json()
        detail = response.get("detail", None)
        if detail in ["Incorrect authentication credentials."]:
            raise Exception(f"{detail} Please check your Splight credentials. Use 'splighthub configure'")
        error = response.get("error", None)
        if error:
            raise Exception(error)
        raise Exception(f"An unknown error ocurred while trying to reach Splight Hub API: {json.dumps(response)}")
    return response

@http_connection
def hub_api_get(*args, **kwargs):
    response = requests.get(*args, **kwargs)
    response = authentication_api_validation(response)
    return response

@http_connection
def hub_api_post(*args, **kwargs):
    response = requests.post(*args, **kwargs)
    response = authentication_api_validation(response)
    return response


    