import requests
from pydantic import BaseSettings
import subprocess
import shutil


class Settings(BaseSettings):
    SPLIGHT_PLATFORM_API_HOST: str
    SPLIGHT_ACCESS_ID: str
    SPLIGHT_SECRET_KEY: str


settings = Settings()


def get_headers(organization=None):
    return {
        "Authorization": f"Splight {settings.SPLIGHT_ACCESS_ID} {settings.SPLIGHT_SECRET_KEY}",
        "X-Organization-ID": organization
    }


def get_organizations():
    print(f"Organizations")
    endpoint = f"{settings.SPLIGHT_PLATFORM_API_HOST}/v2/backoffice/organization/organizations"
    next_page = endpoint
    results = []
    while next_page:
        response = requests.get(
            next_page,
            headers=get_headers()
        )
        assert response.status_code == 200
        results += response.json()["results"]
        next_page = response.json()["next"]
    return [r["id"] for r in results]


if __name__ == "__main__":
    processed_components = []
    for organization in get_organizations():
        running_components = []
        print(f"Organization: {organization}")
        headers = get_headers(organization)
        url = f'{settings.SPLIGHT_PLATFORM_API_HOST}/hub/all/component-versions/?page_size=99999'
        response = requests.get(
            url,
            headers=get_headers(organization)
        )
        response.raise_for_status()
        result = response.json()
        hub_components = result["results"]
        for component in hub_components:
            if component["id"] in processed_components:
                continue
            name = component["name"]
            version = component["version"]

            subprocess.call(
                f"splight hub component pull {name} {version}",
                shell=True
            )

            try:
                with open(f'{name}/{version}/spec.json', 'r') as f:
                    spec_json = f.read()
            except FileNotFoundError:
                print(f'error reading spec.json for {name} {version}')
                processed_components.append(component["id"])
                continue

            if 'bindings' not in spec_json:
                shutil.rmtree(f'{name}')
                continue
            new_spec = spec_json.replace("bindings", "hooks")
            with open(f'{name}/{version}/spec.json', 'w') as f:
                f.write(new_spec)
            subprocess.call(
                f"splight hub component push {name}/{version} -f",
                shell=True
            )
            processed_components.append(component["id"])
            shutil.rmtree(f'{name}')
