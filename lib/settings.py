import os

data_path = "data"
HOME_CFG_PATH = os.path.join(f"{data_path}/home.yaml")

VALID_DEVICE_TYPES = [
    "light",
    "motion_sensor",
    "leak_sensor",
    "temp_sensor",
    "flood",
    "lamp",
    "outlet",
    "controller",
    "blinds",
    "button",
    "door_sensor",
    "vibration_sensor",
    "cube",
]
