# Regroup all lights in the house

import yaml

from errors import UnknownDeviceType, UnknownRoom
from models.device import Device
from mqtt.mqtt import get_devices, rejoin_group, get_groups
from models.home import Home
from settings import HOME_CFG_PATH

with open(HOME_CFG_PATH, "r") as f:
    home_data = yaml.load(f, Loader=yaml.FullLoader)
home = Home.from_dict(home_data)

zigbee_devices = get_devices()
devices = []
for device in zigbee_devices:
    try:
        devices.append(Device.from_zigbee2mqtt_data(device))
    except UnknownDeviceType:
        print(f"Skipping {device['friendly_name']}: Unknown type")

for device in devices:
    try:
        home.place_device(device)
    except UnknownRoom:
        print(f"Skipping {device.name}: Unknown room")

groups = get_groups()
group_names = [i["friendly_name"] for i in groups]

target_room = "downstairs_bathroom"

for area in home.areas:
    area_lights = []
    for room in area.rooms:
        if target_room and room.name != target_room:
            continue
        group_name = f"{room.name}_lights"
        for light in room.get_devices_of_type("light"):
            if group_name not in group_names:
                print(f"Skipping {light} into {group_name}. No group {group_name}")
                continue
            rejoin_group(group_name, light.name)
            area_lights.append(light)

    # area_lights = area.get_devices_of_type('light')
    group_name = f"{area.name}_lights"
    for light in area_lights:
        if group_name not in group_names:
            print(f"Skipping {light} into {group_name}. No group {group_name}")
            continue
        rejoin_group(group_name, light.name)
