from typing import Dict

from cli.settings import SplightCLISettings


def extract_headers(config: SplightCLISettings) -> Dict[str, str]:
    header = f"Splight {config.SPLIGHT_ACCESS_ID} {config.SPLIGHT_SECRET_KEY}"
    return {"Authorization": header}
