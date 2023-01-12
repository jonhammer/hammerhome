import yaml


class ConfigParser(object):

    """Parse different home assistant related configuration files."""

    def __init__(self, config_file_location: str):
        self.config_file_location = config_file_location
        try:
            with open(config_file_location, "r") as f:
                self.data = yaml.load(f, Loader=yaml.FullLoader)
        except FileNotFoundError:
            self.data = None

    def save(self):
        """Save contents of self.data to config_file_location."""
        raise NotImplementedError
