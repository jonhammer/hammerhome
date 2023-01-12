from __future__ import annotations

from typing import List

from errors import UnknownDeviceType
from settings import VALID_DEVICE_TYPES


class Device:
    """Smart home device."""

    def __init__(self, name: str, mac_address: str, device_type: str):
        """

        Args:
            name:
            mac_address:
            device_type:
        """
        self.name = name
        self.mac = mac_address
        self.device_type = device_type

    @staticmethod
    def get_type(device_name):
        possible_types = [i for i in VALID_DEVICE_TYPES if i in device_name]
        possible_types = sorted(possible_types, key=lambda k: len(k), reverse=True)
        if not possible_types:
            raise UnknownDeviceType(f"Unknown device type for {device_name}")
        return possible_types[0]

    @classmethod
    def from_dict(cls, device_data: dict) -> Device:
        """Build device object from dictionary

        Args:
            device_data: dict

        Returns: Device

        """
        device_type = cls.get_type(device_data["name"])
        return Device(device_data["name"], device_data["mac"], device_type)

    @classmethod
    def from_zigbee2mqtt_data(cls, device_data: dict):
        device_name = device_data["friendly_name"]
        device_mac = device_data["ieee_address"]
        device_type = cls.get_type(device_name)
        return Device(device_name, device_mac, device_type)

    def __repr__(self):
        return f"Device(name={self.name},mac={self.mac},device_type={self.device_type})"

    def __eq__(self, other):
        if self.name == other.name:
            return True
        if self.mac == other.mac:
            return True
        return False


class DeviceGroup:
    """Group of devices."""

    def __init__(self, name, devices: List[Device]):
        self.name = name
        self.devices = devices

    def __eq__(self, other):
        if self.name == other.name:
            return True
        return False
