import os
import time
from datetime import datetime

import hassapi as hass
import pytz
import yaml

HOME_DATA_FILE = os.environ.get("HOME_DATA_FILE") or "/conf/apps/home.yaml"
TIMEZONE_NAME = os.environ.get("TIMEZONE_NAME") or "America/New_York"


class HammerHass(hass.Hass):
    """Appdaemon subclass for common hass methods across apps"""

    with open(HOME_DATA_FILE, "r") as f:
        HOME_DATA = yaml.load(f, Loader=yaml.Loader)

    def get_rooms(self):
        """Get all rooms from home.yaml"""
        rooms = []
        for area in self.HOME_DATA["areas"]:
            rooms.append(area["name"])
            if area.get("rooms"):
                for room in area["rooms"]:
                    rooms.append(room["name"])
        return rooms

    def get_room_name(self, entity_id) -> str:
        """Get room name from entity_id"""
        rooms = self.get_rooms()
        possible_rooms = [i for i in rooms if i in entity_id]
        # Sort by length to get the longest match
        possible_rooms.sort(key=len, reverse=True)
        try:
            return possible_rooms[0]
        except KeyError:
            raise ValueError(f"No room found for entity {entity_id}")

    def get_light_data(self, room_name) -> dict:
        """Get light data for a given room."""
        area_name = self.get_area(room_name)
        area_data = next(
            (i for i in self.HOME_DATA["areas"] if i["name"] == area_name), None
        )
        if not area_data:
            raise ValueError(f"No area {area_name}")
        else:
            self.log(f"Got area: {area_data['name']}")

        try:
            lights_data = area_data["lights"]
            self.log(f"Got lights configuration data for {area_data['name']}")
        except KeyError:
            lights_data = {}
            self.log(f"No lights config data for {area_data['name']}")

        room_data = next(
            (i for i in area_data["rooms"] if i["name"] == room_name), None
        )

        # Override area data with more specific room data, if it exists
        if room_data:
            try:
                lights_data.update(room_data["lights"])
                self.log(f"Got lights configuration data for {room_name}")
            except KeyError:
                self.log(f"No lights configuration data for {room_name}")
                pass

        return lights_data

    def is_in_override(self, room_name: str) -> bool:
        """Check if the room has a light override enabled."""
        override = self.get_entity(f"input_boolean.{room_name}_light_override")
        if override.is_state("on"):
            self.log(f"{room_name} lights are in override state")
            return True
        elif override.is_state("off"):
            self.log(f"{room_name} lights are not in override state")
            return False
        raise ValueError(
            f"Invalid room or no override input_boolean defined for {room_name}."
        )

    def restart_home_assistant_timer(self, timer_entity: str):
        """Restart a given homeassistant timer entity."""
        self.log(f"Restarting timer: {timer_entity}")
        entity = self.get_entity(timer_entity)
        entity.call_service("cancel")
        # Race condition? Sometimes timer doesn't restart. Sleep ensures the start is received after the cancel.
        time.sleep(1)
        entity.call_service("start")

    def get_area(self, room_name: str) -> str:
        """Get area name for a given room"""
        for area in self.HOME_DATA["areas"]:
            area_name = area["name"]

            if room_name == area["name"]:
                return area_name

            if area.get("rooms"):
                for room in area["rooms"]:
                    if room_name == room["name"]:
                        return area_name

    def within_required_sun_elevation(self, lights_data: dict) -> bool:
        """Check if the current sun elevation is within the required range."""
        sun_elevation_above = lights_data.get("sun_elevation_above")
        sun_elevation_below = lights_data.get("sun_elevation_below")
        sun = self.get_entity("sun.sun")
        elevation = sun.get_state(attribute="elevation")

        if sun_elevation_above and not elevation > sun_elevation_above:
            self.log(f"Current elevation of {elevation} is below {sun_elevation_above}")
            return False
        if sun_elevation_below and not elevation < sun_elevation_below:
            return False
        return True

    def within_required_time(self, lights_data: dict) -> bool:
        """Check if the current time is within the required range."""
        before = lights_data.get("before")
        after = lights_data.get("after")

        now = self.get_time()

        if before:
            hr, minute = (int(i) for i in before.split(":"))
            before_time = now.replace(hour=hr, minute=minute)
            if now > before_time:
                self.log(
                    f"Current time {now.hour}:{now.minute} is not before required time ({before})"
                )
                return False
        if after:
            hr, minute = (int(i) for i in after.split(":"))
            after_time = now.replace(hour=hr, minute=minute)
            if now < after_time:
                self.log(
                    f"Current time {now.hour}:{now.minute} not after required time ({after})"
                )
                return False

        return True

    @staticmethod
    def get_part_of_day(dt: datetime) -> str:
        """Get the part of the day (for brightness purposes) from a datetime object.
        e.g., one of ['daytime', 'dusk', 'night']
        """
        if 8 <= dt.hour <= 18:  # 8:00AM - 6:59PM
            return "daytime"
        if 19 <= dt.hour <= 20:  # 7:00PM - 8:59PM
            return "dusk"
        if dt.hour >= 20 or dt.hour <= 7:  # 9:01PM 0 - 7:59AM
            return "night"

        raise ValueError(f"Unknown part of day for {dt.hour}")

    @staticmethod
    def get_time() -> datetime:
        """Current time in configured timezone"""
        time_zone = pytz.timezone(TIMEZONE_NAME)
        return datetime.now(tz=time_zone)
