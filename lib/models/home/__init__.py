from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from errors import UnknownRoom
from models.device import Device


@dataclass
class Room:
    """A room within an area."""

    name: str
    devices: List[Device] = field(default_factory=list)

    def get_devices_of_type(self, device_type) -> List[Device]:
        """Get all devices of device_type in Room

        Args:
            device_type:

        Returns:

        """
        if device_type in ["light", "flood", "lamp"]:
            return [
                i for i in self.devices if i.device_type in ["light", "flood", "lamp"]
            ]
        return [i for i in self.devices if i.device_type == device_type]

    def __repr__(self):
        return f"Room(name={self.name})"


@dataclass
class Area:
    """An area in the house, contains one or more rooms."""

    name: str
    rooms: list[Room]

    @classmethod
    def from_dict(cls, data: dict):
        """Build Area object and associated room objects from dict

        Args:
            data: dict

        Returns: Room

        """
        rooms = []
        try:
            for room in data["rooms"]:
                rooms.append(Room(name=room["name"]))
        except KeyError:
            rooms.append(Room(name=data["name"]))
        return cls(data["name"], rooms)

    def get_devices_of_type(self, device_type) -> List[Device]:
        """Get all devices of device_type in the area

        Args:
            device_type:

        Returns:

        """
        devices = []
        for room in self.rooms:
            devices += room.get_devices_of_type(device_type)
        return devices

    def __repr__(self):
        return f"Area(name={self.name},rooms={','.join([i.name for i in self.rooms])})"


@dataclass
class Home:
    """Object to represent entire home.

    The home contains one or more areas, which themselves contain one or more rooms. Devices are assigned per room.
    """

    areas: list[Area]

    @classmethod
    def from_dict(cls, data: dict):
        """Build Home, areas, and rooms from dictionary

        Args:
            data: dict

        Returns: Home

        """
        areas = []
        for area in data["areas"]:
            areas.append(Area.from_dict(area))
        return cls(areas)

    def place_device(self, device: Device, room_name=None):
        """Place device into room within the house"""
        if room_name:
            room = self.get_room(room_name)
            room.devices.append(device)
        else:
            _, room = self.get_area_and_room_of_device(device.name)
            room.devices.append(device)

    def get_area_and_room_of_device(self, room_string: str) -> Tuple[Area, Room]:
        """Return the area and room based on string that contains room name"""
        matches = []
        for area in self.areas:
            for room in area.rooms:
                if room.name.lower() in room_string.lower():
                    matches.append({"area": area, "room": room})

        if not matches:
            raise UnknownRoom(f"No room found for {room_string}")

        if len(matches) > 1:
            matches = sorted(matches, key=lambda k: len(k["room"].name), reverse=True)

        return matches[0]["area"], matches[0]["room"]

    def get_room(self, room_name: str) -> Room:
        """Get room with name matching room_name"""
        for area in self.areas:
            for room in area.rooms:
                if room.name == room_name:
                    return room
        raise UnknownRoom

    def get_room_devices(self, room_name: str) -> List[Device]:
        """Get all devices within a room"""
        room = self.get_room(room_name)
        return room.devices

    def get_rooms(self) -> List[Room]:
        """

        Returns: Get all rooms in the house, regardless of area.

        """
        rooms = []
        for area in self.areas:
            rooms += area.rooms
        return rooms

    def __repr__(self):
        return f"Home(areas={[i.name for i in self.areas]})"
