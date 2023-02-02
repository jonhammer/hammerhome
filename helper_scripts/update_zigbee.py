import json
import time

import paho.mqtt.client as mqtt
from paho.mqtt.publish import single

from helper_scripts.mqtt.mqtt_functions import parse_bytes

CAN_CONTINUE = False
CURRENT_DEVICE = None


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("zigbee2mqtt/bridge/response/device/ota_update/update")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # Zigbee2MQTT:info  2023-01-24 17:48:49: MQTT publish: topic 'zigbee2mqtt/bridge/response/device/ota_update/update', payload '{"data":{"from":null,"id":"game_room_outlet_0","to":null},"status":"ok"}'
    parsed = parse_bytes(msg.payload)
    print(parsed)
    global CAN_CONTINUE
    global CURRENT_DEVICE
    if parsed['data']['id'] == CURRENT_DEVICE:
        if (
            parsed["status"] == "ok"
        ):
            print("setting CAN CONTINUE")
            CAN_CONTINUE = True


print(f"Sleeping for 60 minutes")
time.sleep(60 * 60)

ip = "100.126.3.8"
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(ip, 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
devices = ["bedroom_zrouter_0", "dining_room_flood_1", "kitchen_flood_1", "basement_stairs_light_1"]
client.loop_start()
for device in devices:
    CURRENT_DEVICE = device
    print(f"Updating {device}")
    topic = "zigbee2mqtt/bridge/request/device/ota_update/update"
    data = {"id": device}
    single(topic, payload=json.dumps(data), hostname=ip)
    loops = 0
    print(f"Starting update of {device}...")
    while not CAN_CONTINUE:
        time.sleep(10)
        loops += 1
    CAN_CONTINUE = False
