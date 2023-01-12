import logging

import yaml

from models.home import Home
from settings import HOME_CFG_PATH

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(name)-12s %(levelname)-8s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel("INFO")

with open(HOME_CFG_PATH, "r") as f:
    home_data = yaml.load(f, Loader=yaml.FullLoader)
home = Home.from_dict(home_data)

