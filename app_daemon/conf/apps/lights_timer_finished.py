import os

import HammerHass

HOME_DATA_FILE = os.environ.get("HOME_DATA_FILE") or "/conf/apps/home.yaml"
DEBUG = os.environ.get("DEBUG")


class LightsTimerFinished(HammerHass.HammerHass):
    def initialize(self):
        self.log("---------------------------------------")
        self.log("-- lights_timer_finished.py starting --")
        self.log("---------------------------------------")
        self.listen_event(self.timer_finished_callback, "timer.finished")

    def timer_finished_callback(self, _event_name, data, _kwargs=None):
        """Appdaemon callback for lights timer finished logic"""
        room_name = self.get_room_name(data["entity_id"])

        try:
            occupancy_entity = self.get_entity(f"input_boolean.{room_name}_occupancy")
            if occupancy_entity.is_state("on"):
                self.log(f"{room_name} occupancy is on, will not turn off lights.")
                timer_entity = f"timer.{room_name}_light_timer"
                self.restart_home_assistant_timer(timer_entity)
                return
        except ValueError:
            self.log(f"No occupancy input_boolean defined for {room_name}. Ignoring.")

        if self.is_in_override(room_name):
            self.log(
                f"{room_name} lights are in override state, will not turn off lights."
            )
            return

        light_data = self.get_light_data(room_name)
        if not self.within_required_time(light_data):
            self.log(
                f"{room_name} lights are not within required time, will not turn off lights."
            )
            return

        lights_name = f"light.{room_name}_lights"
        self.log(f"Turning off: {lights_name}")
        try:
            self.turn_off(lights_name, transition=10)
        except AttributeError:
            self.log(f"Could not turn off {lights_name}")

