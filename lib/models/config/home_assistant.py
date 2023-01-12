import logging
from models.home import Home, Room, Area
from models.yaml_config import ConfigParser


class HomeAssistantConfig(ConfigParser):
    """Python representation of a home-assistant configuration."""


class GroupConfig(ConfigParser):
    """Python representation of a home-assistant groups configuration."""

    def add_occupancy_groups(self, home: Home):
        """Define occupancy groups for entire home."""

        for area in home.areas:
            for room in area.rooms:
                self.add_occupancy_group(room)

    def add_occupancy_group(self, room: Room):
        """Define occupancy groups for individual room."""
        occupancy_group_id = f"{room.name}_occupancy"
        occupancy_group_name = f"{room.name} occupancy"
        if occupancy_group_id in self.data:
            print(f"{occupancy_group_id} already in groups config. Skipping.")
            return

        group_devices = room.get_devices_of_type("motion_sensor")
        group_entities = [f"binary_sensor.{i.name}_occupancy" for i in group_devices]
        self.data[occupancy_group_id] = {
            "entites": group_entities,
            "name": occupancy_group_name,
        }
        print(f"Added {occupancy_group_id} to groups configuration.")


class AreaDashboard(ConfigParser):
    """Dashboard for an area"""

    def generate_data(self, area: Area):
        """Regenerate dashboard data."""
        self.data = {"title": area.name, "views": [{"cards": []}]}
        for room in area.rooms:
            lights = room.get_devices_of_type("light")
            card_data = {
                "entities": [f"light.{i.name}" for i in lights],
                "title": room.name,
                type: "entities",
            }
            self.data["views"][0]["cards"].append(card_data)
