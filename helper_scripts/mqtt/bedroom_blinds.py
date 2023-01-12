# Simple script to fix my ikea fyrtur blinds that are constantly glitching out

import json
from time import sleep

import yaml
from paho.mqtt.publish import single

from models.home import Home
from mqtt.mqtt import get_devices, ip
from settings import HOME_CFG_PATH

with open(HOME_CFG_PATH, "r") as f:
    home_data = yaml.load(f, Loader=yaml.FullLoader)
home = Home.from_dict(home_data)

zigbee_devices = get_devices()
blind_macs = [
    {"mac": "0x804b50fffeab8952", "name": "front_blinds"},
    {"mac": "0xcc86ecfffe9523b3", "name": "sarah_blinds"},
    {"mac": "0x84fd27fffedf9239", "name": "back_blinds"},
    {"mac": "0xcc86ecfffef9df21", "name": "jon_blinds"},
]

blinds = [
    i
    for i in zigbee_devices
    if [x for x in blind_macs if x["mac"] == i["ieee_address"]]
]


def reconfigure(mac):
    friendly_name = next((i["name"] for i in blind_macs if i["mac"] == mac), None)
    topic = f"zigbee2mqtt/bridge/request/device/rename"
    payload = {"from": mac, "to": "abcdef", "homeassistant_rename": True}
    single(topic, payload=json.dumps(payload), hostname=ip)
    sleep(2)
    print(f"Renaming {mac} to {friendly_name}")
    payload = {"from": mac, "to": friendly_name, "homeassistant_rename": True}
    single(topic, payload=json.dumps(payload), hostname=ip)


def remove(blind):
    pass


for mac_address in [i["mac"] for i in blind_macs]:
    reconfigure(mac_address)
    sleep(2)
