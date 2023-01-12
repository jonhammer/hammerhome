import os
import re

import hassapi as hass
import yaml

ROOM_RE = r"timer\.(.*)_light_timer"
HOME_DATA_FILE = os.environ.get("HOME_DATA_FILE") or "/conf/apps/home.yaml"
DEBUG = os.environ.get("DEBUG")


class LightsTimerFinished(hass.Hass):

    with open(HOME_DATA_FILE, "r") as f:
        HOME_DATA = yaml.load(f, Loader=yaml.Loader)

    def initialize(self):
        self.log("---------------------------------------")
        self.log("-- lights_timer_finished.py starting --")
        self.log("---------------------------------------")
        self.listen_event(self.timer_finished_callback, "timer.finished")

    def timer_finished_callback(self, _event_name, data, _kwargs=None):
        """Appdaemon callback for lights timer finished logic"""
        room_name = re.search(ROOM_RE, data["entity_id"]).group(1)
        lights_name = f"light.{room_name}_lights"
        self.log(f"Turning off: {lights_name}")
        try:
            self.turn_off(lights_name, transition=10)
        except AttributeError:
            self.log(f"Could not turn off {lights_name}")
