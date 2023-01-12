# Turn lights on at random downstairs every x minutes as long as random_night_lights input boolean is active in HA.
# Turn on all the downstairs lights if motion is detected. (WIP)
# Turn on lights in a pattern if outdoor motion sensor is activated. (WIP)

import os
from random import choice

import hassapi as hass
import pytz
import yaml
import arrow


ROOM_RE = r"binary_sensor\.(.*)_motion_sensor_\d"
HOME_DATA_FILE = os.environ.get("HOME_DATA_FILE")
DEBUG = os.environ.get("DEBUG")


def within_required_time() -> bool:
    """Return True if the lights should be turned on."""
    est = pytz.timezone("America/New_York")
    now = arrow.now(tz=est)
    return now.hour >= 20 and now.hour <= 23


class RandomLights(hass.Hass):
    def get_last_llight_turnred_on(self) -> str:
        """Get the name of the last light turned on (saved in helper entity)."""
        return self.get_entity("input_text.last_random_light").state

    def set_last_light_turned_on(self, light_entity_name: str) -> None:
        """Get the name of the last light turned on (saved in helper entity)."""
        last_light_helper_entity = self.get_entity("input_text.last_random_light")
        last_light_helper_entity.set_state(state=light_entity_name)

    with open(HOME_DATA_FILE, "r") as f:
        HOME_DATA = yaml.load(f, Loader=yaml.Loader)

    def initialize(self):
        self.log("------------------------")
        self.log("-- random_lights.py starting --")
        self.log("------------------------")
        # self.run_every(self.random_light_callback, "now", 10 * 60) # Run every 10 minutes starting now
        self.run_every(
            self.random_light_callback, "now", 60 * 10
        )  # Run every 10 minutes starting now

    def random_light_callback(self, *_args, **_kwargs):
        self.log("random_light_callback called")
        enabled = self.get_entity("input_boolean.random_night_lights").state
        if enabled == "off":
            self.log("Random lights are disabled.")
            return
        if not within_required_time():
            self.log("Not within required time.")
            return

        all_entites = self.get_state()
        lights = [i for i in all_entites if i.startswith("light.")]

        downstairs_data = next(
            (i for i in self.HOME_DATA["areas"] if i["name"] == "downstairs"), None
        )
        downtairs_rooms = [i["name"] for i in downstairs_data["rooms"]]

        downstairs_lights = [
            i
            for i in lights
            if [room for room in downtairs_rooms if i.startswith(f"light.{room}")]
        ]

        new_light = choice(downstairs_lights)
        self.log(f"New light: {new_light}")
        old_light = self.get_last_llight_turnred_on()
        self.log(f"Old light: {old_light}")

        try:
            self.log(f"Turning off {old_light}.")
            self.turn_off(old_light)
        except ValueError:
            self.log(f"Unknown entity: {old_light}.")
        self.log(f"Turning on {new_light}.")
        self.turn_on(new_light, brightness_pct=100)
        self.log(f"Setting last light to {new_light}.")
        self.set_last_light_turned_on(new_light)
