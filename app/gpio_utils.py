"""GPIO Module utils"""
from time import sleep
from typing import Union

from app import config

try:
    # checks if you have access to RPi.GPIO, which is available inside RPi
    import RPi.GPIO as GPIO
except:  # pylint: disable=bare-except
    # In case of exception, you are executing your script outside of RPi, so import Mock.GPIO
    import Mock.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


def get_channels() -> Union[list, str]:
    """Return channels from config"""
    if config.MULTIPLE_RELAY:
        return config.RELAY_CHANNELS
    return config.MAIN_RELAY


def setup():
    """Setup GPIO channel(s) for relay"""
    GPIO.setup(get_channels(), GPIO.OUT, initial=GPIO.LOW)


def turn_on():
    """Turn on lights"""
    GPIO.output(get_channels(), 0)


def turn_off():
    """Turn off lights"""
    GPIO.output(get_channels(), 1)


def is_on():
    """check if pin/light is on"""
    if not isinstance(get_channels(), list):
        _channels = [get_channels()]
    for channel in _channels:
        if not GPIO.input(channel):
            return False
    return True


def change_mode():
    """Change mode, 1 cycle"""
    if not is_on():
        turn_on()
        sleep(0.5)
    turn_off()
    sleep(0.5)
    turn_on()


def change_color(new_color: str) -> str:
    """Change color of lights"""
    current_color = config.current_color()
    cycles = config.MODE_MAP.get(current_color) - config.MODE_MAP.get(new_color)
    for _ in range(cycles):
        change_mode()
        sleep(0.2)
    config.set_color(new_color)
