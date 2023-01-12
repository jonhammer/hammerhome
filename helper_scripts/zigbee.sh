#!/bin/bash
# additional dependencies: graphviz imagemagick

# put temporal files in ram filesystem
file="/tmp/networkmap"
ROOT="0x000000000"  # put your coordinator here
mqtthost="100.123.227.109" # change if your mosquitto is on another host
#user="mqtt-username"
#pass="mqtt-password"
#~ echo $fechahora

#mosquitto_sub -h $mqtthost -u $user -P $pass -t zigbee2mqtt/bridge/networkmap/graphviz -C 1 >${file}routes.dot &
#mosquitto_pub -h $mqtthost -u $user -P $pass -t zigbee2mqtt/bridge/networkmap/routes -m graphviz
mosquitto_sub -h $mqtthost -t zigbee2mqtt/bridge/networkmap/graphviz -C 1 >${file}routes.dot &
mosquitto_pub -h $mqtthost -t zigbee2mqtt/bridge/networkmap/routes -m graphviz

# wait until mosquitto_sub ends
wait

# generate graphic with graphviz (change to short texts with sed)
cat ${file}routes.dot|sed -e 's/Xiaomi Aqara temperature, humidity and pressure sensor/AqaraTHP/g'|sed -e 's/Xiaomi Mi\/Aqara smart home cube/AqaraCube/g'|sed -e 's/Xiaomi Aqara double key wireless wall switch/AqaraDoubleSwitch/g'|\
   dot -Kneato -Groot=$ROOT -Goverlap=false -Gnodesep=1 -Granksep=1 -Tsvg > ${file}routes.svg

# display with imageMagick eommand
#display ${file}routes.svg &
open -a "Google Chrome" ${file}routes.svg
