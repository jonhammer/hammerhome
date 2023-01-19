import os

import yaml
import HammerHass

HOME_DATA_FILE = os.environ.get("HOME_DATA_FILE") or "/conf/apps/home.yaml"
TIMEZONE_NAME = os.environ.get("TIMEZONE_NAME") or "America/New_York"


class MotionLight(HammerHass.HammerHass):
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

        room_name = self.get_room_name(data["entity_id"])

        timer_entity = f"timer.{room_name}_light_timer"
        light_entity = f"light.{room_name}_lights"

        self.log("Motion event detected")
        self.log("----------------------")
        self.log(f"Entity_id: {data['entity_id']}")
        self.log(f"Room: {room_name}")
        self.log(f"Timer: {timer_entity}")
        self.log(f"Entity: {light_entity}")

        lights_data = self.get_light_data(room_name)

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
        now = self.get_time()
        self.LAST_TRIGGERED[room_name] = now

    def get_brightness(self, room_name, lights_data: dict) -> int:
        """Get brightness for a given room."""
        now = self.get_time()
        last_trigger_time = self.LAST_TRIGGERED.get(room_name)
        if not last_trigger_time:
            last_trigger_time = now.replace(year=1970)

        current_part_of_day = self.get_part_of_day(now)

        # Ensure we only modify brightness once per time period (morning/dusk/night). Otherwise keep current brightness.
        if (now - last_trigger_time).total_seconds() < 43000:
            last_triggered_part_of_day = self.get_part_of_day(last_trigger_time)

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
