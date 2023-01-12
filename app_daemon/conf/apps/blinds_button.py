import re

import hassapi as hass

ROOM_RE = r"sensor\.(.*)_lights_button_\d"


class BlindsButton(hass.Hass):
    def initialize(self):
        self.log("------------------------------")
        self.log("-- light_button.py starting --")
        self.log("------------------------------")
        self.listen_event(self.button_press_callback, "state_changed")

    def button_press_callback(self, _event_name, data, _kwargs=None):
        if not ("button" in data["entity_id"]):
            return

        state = data["new_state"]["state"]
        if state not in ["on", "brightness_move_up"]:
            return

        self.log(f"{data['entity_id']} pressed")

        room = re.search(ROOM_RE, data["entity_id"]).group(1)
        lights = f"light.{room}_lights"
        self.log(f"Room: {room}")
        self.log(f"Blindss: {lights}")

        if state == "on":
            self.log(f"Toggling {lights}")
            self.toggle(lights)

        if state == "brightness_move_up":
            self.log(f"Brightness modification requested for {lights}")
            light_entity = self.get_entity(lights)
            if light_entity.state == "off":
                self.log(f"Blinds is off, currently, turning to low brightness")
                desired_brightness = 10
            else:
                current_brightness = light_entity.attributes["brightness"]
                self.log(f"Current brightness: {current_brightness}")
                desired_brightness = get_next_brightness(current_brightness)
            self.log(f"Desired brightness: {desired_brightness}")
            self.turn_on(lights, brightness=desired_brightness)
