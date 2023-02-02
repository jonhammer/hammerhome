# Simple script to rejoin a device to a group via MQTT

import json
from json import JSONDecodeError
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


def main():
    devices = get_devices()

    friendly_names = [device["friendly_name"] for device in devices if device.get('friendly_name')]
    offline_devices = {'lights': [], 'devices': [], 'total': 0}
    for name in friendly_names[1:]:
        availability = simple(f"zigbee2mqtt/{name}/availability", hostname=ip)
        status = parse_bytes(availability.payload)
        if status["state"] == 'offline':
            if [i for i in ['flood', 'light'] if i in name]:
                offline_devices['lights'].append(name)
            else:
                offline_devices['devices'].append(name)

    if offline_devices['lights']:
        print("Offline lights")
        print("--------------")
        for light in offline_devices['lights']:
            print(f" - {light}")

    if offline_devices['devices']:
        print("")
        print("Offline devices")
        print("--------------")
        for device in offline_devices['devices']:
            print(f" - {device}")

    offline_devices['total'] = len(offline_devices['lights']) + len(offline_devices['devices'])
    print(f"Total offline devices: {offline_devices['total']}")

    save_file_location = '/home/jon/offline_zigbee_devices.json'

    print("")

    try:
        with open(save_file_location, 'r') as f:
            saved_devices = json.load(f)
        print("Devices that are newly offline")
        print("----------------------------------------")
        count = 0
        for device in offline_devices['lights']:
            if device not in saved_devices['lights']:
                count += 1
                print(f" - {device}")
        for device in offline_devices['devices']:
            if device not in saved_devices['devices']:
                count += 1
                print(f" - {device}")
        print(f"Previous total offline devices: {saved_devices['total']}")
    except (JSONDecodeError, FileNotFoundError):
        print("No saved devices found")


    with open(save_file_location, 'w') as f:
        json.dump(offline_devices, f)

    # Pretty print the json for device

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

if __name__ == '__main__':
    main()
