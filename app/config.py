"""Configuration for light controller"""
from configparser import ConfigParser

MULTIPLE_RELAY = False

MAIN_RELAY = 14

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

# map colors to mode number, per SR Smith documentation
MODE_MAP = {
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

current = ConfigParser()
current.read("currents.ini")


def current_color():
    """get the current color from ini file"""
    return INT_MODE_MAP.get(current.get("current_values", "current_color"))


def set_color(value):
    """set the current color in the ini file"""
    current.set("current_values", "current_color", MODE_MAP.get(value))
