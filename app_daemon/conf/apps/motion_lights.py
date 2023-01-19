import os
import re
import time
from datetime import datetime

# pylint: disable=import-error
import hassapi as hass
import pytz
import yaml

ROOM_RE = r"binary_sensor\.(.*)_motion_sensor_\d"
HOME_DATA_FILE = os.environ.get("HOME_DATA_FILE") or "/conf/apps/home.yaml"
TIMEZONE_NAME = os.environ.get("TIMEZONE_NAME") or "America/New_York"


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


def get_time() -> datetime:
    """Current time in configured timezone"""
    time_zone = pytz.timezone(TIMEZONE_NAME)
    return datetime.now(tz=time_zone)


class MotionLight(hass.Hass):
    """Appdaemon class for motion controlled lights"""

    LAST_TRIGGERED = {}

    with open(HOME_DATA_FILE, "r") as f:
        HOME_DATA = yaml.load(f, Loader=yaml.Loader)

    def initialize(self):
        """Appdaemon event listener"""
        self.log("------------------------")
        self.log("-- motion_lights.py starting --")
        self.log("------------------------")
        self.listen_event(self.motion_detected_callback, "state_changed")

    def motion_detected_callback(self, _event_name, data, _kwargs=None):
        """Appdaemon callback for motion lights logic"""
        if not (
            "motion_sensor" in data["entity_id"] and "occupancy" in data["entity_id"]
        ):
            return

        new_state = data["new_state"]["state"]

        if not new_state == "on":
            return

        room_name = re.search(ROOM_RE, data["entity_id"]).group(1)

        timer_entity = f"timer.{room_name}_light_timer"
        light_entity = f"light.{room_name}_lights"

        self.log("Motion event detected")
        self.log("----------------------")
        self.log(f"Entity_id: {data['entity_id']}")
        self.log(f"Room: {room_name}")
        self.log(f"Timer: {timer_entity}")
        self.log(f"Entity: {light_entity}")

        # Get area/room lights data
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

        # Run checks
        try:
            if self.is_in_override(room_name):
                self.log(
                    f"{room_name} lights are in override state, will not turn on lights."
                )
                return
        except ValueError:
            self.log(f"No override input_boolean defined for {room_name}. Ignoring.")
            pass

        if not self.within_required_sun_elevation(lights_data):
            self.log(
                f"{room_name} lights are outside required sun elevation, will not turn on lights."
            )
            return

        if not self.within_required_time(lights_data):
            self.log(
                f"{room_name} lights are outside required time, will not turn on lights."
            )
            return

        # Get brightness, turn on lights, reset timers
        brightness = self.get_brightness(room_name, lights_data)
        self.log(f"Brightness requested: {brightness}")

        if brightness:
            self.log(f"Turning on {light_entity} to brightness of {brightness}%")
            self.turn_on(light_entity, brightness_pct=brightness)
        else:
            self.log(f"Turning on {light_entity}")
            self.turn_on(light_entity)
        self.restart_home_assistant_timer(timer_entity)

        # Update last triggered time
        now = get_time()
        self.LAST_TRIGGERED[room_name] = now

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

        now = get_time()

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

    def get_brightness(self, room_name, lights_data: dict) -> int:
        """Get brightness for a given room."""
        now = get_time()
        last_trigger_time = self.LAST_TRIGGERED.get(room_name)
        if not last_trigger_time:
            last_trigger_time = now.replace(year=1970)

        current_part_of_day = get_part_of_day(now)

        # Ensure we only modify brightness once per time period (morning/dusk/night). Otherwise keep current brightness.
        if (now - last_trigger_time).total_seconds() < 43000:
            last_triggered_part_of_day = get_part_of_day(last_trigger_time)

            if current_part_of_day == last_triggered_part_of_day:
                self.log("Last triggered recently, not modifying brightness level")
                return 0

        # Check config for brightness levels, otherwise use defaults:
        # Day = 100
        # Dusk = 50
        # Night = 10
        if current_part_of_day == "daytime":
            daytime_brightness = lights_data.get("daytime_brightness")
            if daytime_brightness:
                return daytime_brightness
            else:
                return 100

        if current_part_of_day == "dusk":
            self.log("7:00PM - 8:59PM")
            dusk_brightness = lights_data.get("dusk_brightness")
            if dusk_brightness:
                return dusk_brightness
            else:
                return 50

        if current_part_of_day == "night":
            self.log("9:01PM - 7:59AM")
            night_brightness = lights_data.get("night_brightness")
            if night_brightness:
                return night_brightness
            else:
                return 10
