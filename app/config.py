"""Configuration for light controller"""
from configparser import ConfigParser
from os.path import exists
from shutil import copyfile

MULTIPLE_RELAY = False

MAIN_RELAY = 17

RELAY_CHANNELS = []

# COLOR CONSTANTS
WHITE = "white"
BLUE = "blue"
GREEN = "green"
RED = "red"
AMBER = "amber"
MAGENTA = "magenta"

# special modes
SOFT = "soft"  # soft color change
FLASH = "flash"  # flash color change

# unknown, never set
UNKNOWN = "unknown"

# map colors to mode number, per SR Smith documentation
MODE_MAP = {
    UNKNOWN: 0,
    SOFT: 1,
    WHITE: 2,
    BLUE: 3,
    GREEN: 4,
    RED: 5,
    AMBER: 6,
    MAGENTA: 7,
    FLASH: 8,
}

INT_MODE_MAP = {k: v for v, k in MODE_MAP.items()}

CONFIG_FILE = "app/currents.ini"

current = ConfigParser()
# current.read(CONFIG_FILE)


def setup_config():
    """Copy template for config if a config does not exist"""
    if not exists(CONFIG_FILE):
        copyfile("app/currents_template.ini", CONFIG_FILE)
    current.read(CONFIG_FILE)


def current_color():
    """get the current color from ini file"""
    current.read(CONFIG_FILE)
    return INT_MODE_MAP.get(int(current.get("current_values", "current_color")))


def set_color(value):
    """set the current color in the ini file"""
    current.set("current_values", "current_color", str(MODE_MAP.get(value)))
    with open(CONFIG_FILE, "w", encoding="utf8") as configfile:
        current.write(configfile)


def current_power():
    """get the current power from ini file"""
    current.read(CONFIG_FILE)
    return bool(int(current.get("current_values", "powered_on")))


def set_power(_bool: bool):
    """Set power in ini, True is on, False is off"""
    value = 1 if _bool else 0
    current.set("current_values", "powered_on", str(value))
    with open(CONFIG_FILE, "w", encoding="utf8") as configfile:
        current.write(configfile)


class Settings:
    """Class to returns settings"""

    @property
    def port(self):
        """Return port"""
        return current.get("current_values", "port")

    @property
    def username(self):
        """Return username"""
        return current.get("current_values", "username")

    @property
    def password(self):
        """Return password"""
        return current.get("current_values", "password")

    @property
    def secret_key(self):
        """Return secret_key"""
        return current.get("current_values", "secret_key")
