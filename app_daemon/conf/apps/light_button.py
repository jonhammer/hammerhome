import re

import hassapi as hass

ROOM_RE = r"sensor\.(.*)_lights_button_\d"


def get_next_brightness(current_brightness_value: int) -> int:
    """Get the next brightness value for a light. Cycle from low -> medium -> high."""
    if current_brightness_value <= 126:
        return 127
    if 255 > current_brightness_value >= 127:
        return 255
    if current_brightness_value == 255:
        return 10
    raise ValueError(f"Unknown brightness value: {current_brightness_value}")


class LightButton(hass.Hass):
    def initialize(self):
        self.log("------------------------------")
        self.log("-- light_button.py starting --")
        self.log("------------------------------")
        self.listen_event(self.button_press_callback, "state_changed")

    def button_press_callback(self, _event_name, data, _kwargs=None):
        """Handle a button press event."""
        if not ("button" in data["entity_id"]):
            return

        state = data["new_state"]["state"]
        if state not in ["on", "brightness_move_up", "single", "hold"]:
            self.log(f"Unknown state for button press: {state}")
            return

        self.log(f"{data['entity_id']} pressed")

        room = re.search(ROOM_RE, data["entity_id"]).group(1)
        lights = f"light.{room}_lights"
        self.log(f"Room: {room}")
        self.log(f"Lights: {lights}")

        if state in ["on", "single"] :
            self.log(f"Toggling {lights}")
            self.toggle(lights)

        if state in ["brightness_move_up", "hold"]:
            self.log(f"Brightness modification requested for {lights}")
            light_entity = self.get_entity(lights)
            if light_entity.state == "off":
                self.log(f"Light is off, currently, turning to low brightness")
                desired_brightness = 10
            else:
                current_brightness = light_entity.attributes["brightness"]
                self.log(f"Current brightness: {current_brightness}")
                desired_brightness = get_next_brightness(current_brightness)
            self.log(f"Desired brightness: {desired_brightness}")
            self.turn_on(lights, brightness=desired_brightness)
