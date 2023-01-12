from pprint import pprint

from requests import get

base_url = "https://homeassistant.homelab.jph.dev/api/"
token = "REDACTED"
headers = {
    "Authorization": f"Bearer {token}",
    "content-type": "application/json",
}

service_url = base_url + "services"
states_url = base_url + "states"

services = get(service_url, headers=headers).json()
states = get(states_url, headers=headers).json()
