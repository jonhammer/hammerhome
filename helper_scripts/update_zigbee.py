import json
import time

import paho.mqtt.client as mqtt
from paho.mqtt.publish import single

from mqtt.mqtt import parse_bytes

CAN_CONTINUE = False


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("zigbee2mqtt/bridge/log")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    global CAN_CONTINUE
    if (
        parse_bytes(msg.payload)["meta"]["status"] == "update_failed"
        or parse_bytes(msg.payload)["meta"]["status"] == "update_succeeded"
    ):
        print("setting CAN CONTINUE")
        CAN_CONTINUE = True


ip = "100.123.227.109"
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(ip, 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
devices = ["game_room_light_1", "game_room_light_3", "game_room_light_5"]
client.loop_start()
for device in devices:
    print(f"Updating {device}")
    topic = "zigbee2mqtt/bridge/request/device/ota_update/update"
    data = {"id": device}
    single(topic, payload=json.dumps(data), hostname=ip)
    loops = 0
    while not CAN_CONTINUE:
        seconds = 90 - (loops * 10)
        if seconds > 0:
            print(f"Waiting ({seconds} seconds remaining until timeout)...")
        else:
            print("Update in progress...")
        time.sleep(10)
        loops += 1
    CAN_CONTINUE = False
