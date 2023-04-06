import os
from typing import Optional

import HammerHass

HOME_DATA_FILE = os.environ.get("HOME_DATA_FILE", "/conf/apps/home.yaml")
TIMEZONE_NAME = os.environ.get("TIMEZONE_NAME", "America/New_York")


class MotionLight(HammerHass.HammerHass):
    """Appdaemon class for motion-controlled lights"""

    LAST_TRIGGERED = {}

    def initialize(self) -> None:
        """Appdaemon event listener"""
        self.log("------------------------")
        self.log("-- motion_lights.py starting --")
        self.log("------------------------")
        self.listen_event(self.motion_detected_callback, "state_changed")

    def motion_detected_callback(self, _event_name: str, data: dict, _kwargs: Optional[dict] = None) -> None:
        """Appdaemon callback for motion lights logic"""

        if "motion_sensor" in data["entity_id"] and "occupancy" in data["entity_id"]:
            is_presence_sensor = False
        elif "presence_sensor" in data["entity_id"] and "event" in data["entity_id"]:
            is_presence_sensor = True
        else:
            return

        new_state = data["new_state"]["state"]

        room_name = self.get_room_name(data["entity_id"])
        lights_data = self.get_light_data(room_name)

        if (is_presence_sensor and new_state == "leave") or (not is_presence_sensor and new_state != "on"):
            return

        timer_entity = f"timer.{room_name}_light_timer"
        light_entity = f"light.{room_name}_lights"

        self.log("Motion event detected\n----------------------")
        self.log(f"Entity ID: {data['entity_id']}\nRoom: {room_name}\nTimer: {timer_entity}\nEntity: {light_entity}")

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

        brightness = self.get_brightness(room_name, lights_data)
        self.log(f"Brightness requested: {brightness}")

        if brightness:
            self.log(f"Turning on {light_entity} to brightness of {brightness}%")
            self.turn_on(light_entity, brightness_pct=brightness)
        else:
            self.log(f"Turning on {light_entity}")
            self.turn_on(light_entity)
        self.restart_home_assistant_timer(timer_entity)

        now = self.get_time()
        self.LAST_TRIGGERED[room_name] = now

    def get_brightness(self, room_name: str, lights_data: dict) -> int:
        """Get brightness for a given room."""
        now = self.get_time()
        last_trigger_time = self.LAST_TRIGGERED.get(room_name, now.replace(year=1970))

        current_part_of_day = self.get_part_of_day(now)
        last_triggered_part_of_day = self.get_part_of_day(last_trigger_time)

        if (now - last_trigger_time).total_seconds() < 43000 and current_part_of_day == last_triggered_part_of_day:
            self.log("Last triggered recently, not modifying brightness level")
            return 0

        brightness_mapping = {
            "daytime": lights_data.get("daytime_brightness", 100),
            "dusk": lights_data.get("dusk_brightness", 50),
            "night": lights_data.get("night_brightness", 10),
        }

        return brightness_mapping.get(current_part_of_day, 0)

            
