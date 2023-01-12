import yaml

from models.config import ConfigParser
from models.errors import DuplicateDeviceError


class ZigbeeDeviceGroup(object):
    """Represents a group of Zigbee devices. Exposed to homeassistant as a single device."""

    def __init__(self, group_id: int, name: str):
        self.group_id = str(group_id)
        self.name = name
        self.devices = []

    def add_device(self, device_name):
        """Add device to group if it is not already present.

        Args:
            device_name:
        """
        if device_name not in self.devices:
            self.devices.append(device_name)


class ZigbeeDevice(object):
    """Device in the zigbee2mqtt configuration."""

    def __init__(self, mac, name):
        self.mac = mac
        self.name = name

    def to_dict(self) -> dict:
        """Dict representation of ZigbeeDevice

        Returns: dict

        """
        return {"name": self.name, "mac": self.mac}


class ZigbeeConfig(ConfigParser):
    """Python representation of zigbee2mqtt configuration file."""

    def __init__(self, config_file_location: str):
        super().__init__(config_file_location)
        self.devices = []
        self.groups = []

    def get_device(self, name_or_mac: str) -> ZigbeeDevice:
        """Get ZigbeeDevice matching the name_or_mac.

        Args:
            name_or_mac:

        Returns: ZigbeeDevice or None

        """
        matched_devices = [
            i for i in self.devices if i.name == name_or_mac or i.mac == name_or_mac
        ]
        if len(matched_devices) > 1:
            raise DuplicateDeviceError(
                f"Found more than one device matching name or mac: {name_or_mac}"
            )
        elif len(matched_devices) == 1:
            return matched_devices[0]

    def parse_config(self):
        """Parse zigbee2mqtt configuration file.

        Sets all associated Device and Group objects.

        """
        for device_mac, data in self.data["devices"].items():
            self.devices.append(ZigbeeDevice(device_mac, data["friendly_name"]))

        for group_id, data in self.data["groups"].items():
            group = ZigbeeDeviceGroup(int(group_id), data["friendly_name"])
            for device_name in data["devices"]:
                device = self.get_device(device_name)
                group.devices.append(device)
            self.groups.append(group)
