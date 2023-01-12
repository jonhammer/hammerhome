# Simple script to rejoin a device to a group via MQTT

import json
from time import sleep

from paho.mqtt.publish import single
from paho.mqtt.subscribe import simple

ip = "100.126.3.8"
# payload = {"state": "ON"}

# payload = {"group": "kitchen_lights", "device": "kitchen_flood_0"}
# single(topic, payload=json.dumps(payload), hostname=ip)


def get_groups():
    topic = f"zigbee2mqtt/bridge/groups"
    groups = simple(topic, hostname=ip)
    parsed = parse_bytes(groups.payload)
    return parsed


def get_devices():
    topic = f"zigbee2mqtt/bridge/devices"
    devices = simple(topic, hostname=ip)
    parsed = parse_bytes(devices.payload)
    return parsed


def parse_bytes(bytes):
    bytes.decode("utf8").replace("'", '"')
    return json.loads(bytes)


def rejoin_group(group_name, device):
    topic = f"zigbee2mqtt/bridge/request/group/members/remove"
    payload = {"group": group_name, "device": device}
    print(f"Removing {device} from {group_name}")
    single(topic, payload=json.dumps(payload), hostname=ip)
    sleep(2)
    print(f"Adding {device} to {group_name}")
    topic = f"zigbee2mqtt/bridge/request/group/members/add"
    single(topic, payload=json.dumps(payload), hostname=ip)
    sleep(2)


# num_devices = 4
# area = 'upstairs'
# room = 'sarah_office'
# light_type = 'lamp'
#
# device_prefix = f'{room}_{light_type}'
# devices = [f'{device_prefix}_{i}' for i in range(num_devices)]
# groups = [f'{room}_lights', f'{area}_lights']
# for group_name in groups:
#     for device in devices:
#         rejoin_group(group_name, device)
#

# scene_data = {
#     'ID': 0,
#     'state': 'ON',
#     'brightness': 254
# }
# topic = f"zigbee2mqtt/kitchen_lights/set"
# payload = {
#     "scene_store": 1
# }
# single(topic, payload=json.dumps(payload), hostname=ip)
