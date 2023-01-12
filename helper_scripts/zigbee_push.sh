scp /home/jon/hammernet/home_assistant/has_config/zigbee2mqtt/configuration.yaml pi@zigbee:/opt/zigbee2mqtt/data/configuration.yaml
ssh zigbee "sudo systemctl restart zigbee2mqtt.service"