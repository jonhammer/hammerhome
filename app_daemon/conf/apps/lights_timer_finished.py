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
        try:
            room_name = self.get_room_name(data["entity_id"])
        except ValueError:
            self.log(f"Could not find room for {data['entity_id']}")
            return

        light_data = self.get_light_data(room_name)
        if not self.within_required_time(light_data):
            self.log(
                f"{room_name} lights are not within required time, will not turn off lights."
            )
            return

        timer_entity = f"timer.{room_name}_light_timer"

        blocking_entities = light_data.get("block_off_entities", {})
        for blocking_entity_name, state in blocking_entities.items():
            blocking_entity = self.get_entity(blocking_entity_name)
            if blocking_entity.is_state(state):
                self.log(f"{blocking_entity_name} is {state}, will not turn off lights.")
                self.restart_home_assistant_timer(timer_entity)
                return

        if self.is_in_override(room_name):
            self.log(
                f"{room_name} lights are in override state, will not turn off lights."
            )
            self.restart_home_assistant_timer(timer_entity)
            return

        lights_name = f"light.{room_name}_lights"
        self.log(f"Turning off: {lights_name}")
        try:
            self.turn_off(lights_name, transition=10)
        except AttributeError:
            self.log(f"Could not turn off {lights_name}")

