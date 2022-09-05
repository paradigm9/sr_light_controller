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

channels = config.RELAY_CHANNELS if config.MULTIPLE_RELAY else config.MAIN_RELAY


def setup():
    """Setup GPIO channel(s) for relay"""
    GPIO.setup(channels, GPIO.OUT, initial=GPIO.LOW)


def turn_on():
    """Turn on lights"""
    GPIO.output(channels, 0)


def api_turn_on():
    """Used for single call from API to turn on"""
    turn_on()
    config.set_power(True)


def turn_off():
    """Turn off lights"""
    GPIO.output(channels, 1)


def api_turn_off():
    """Used for single call from API to turn off"""
    turn_off()
    config.set_power(False)


def is_on():
    """check if pin/light is on"""
    if not isinstance(channels, list):
        _channels = [channels]
    for channel in _channels:
        if not GPIO.input(channel):
            return False
    return True


def cycle_on_off():
    """Cycle power on off"""
    turn_on()
    sleep(0.5)
    turn_off()
    sleep(0.5)


def change_mode():
    """Change mode, 1 cycle"""
    if not is_on():
        turn_on()
        sleep(0.5)
    turn_off()
    sleep(0.5)
    turn_on()
    sleep(0.5)


def reset():
    """Reset lights, this will result in lights being in mode 1/soft color change"""
    turn_off()
    sleep(5)
    for _ in range(3):
        cycle_on_off()
    sleep(5)
    turn_on()
    config.set_color(config.SOFT)
    config.set_power(True)


def change_color(new_color: str) -> str:
    """Change color of lights"""
    current_color = config.current_color()
    cycles = config.MODE_MAP.get(current_color) - config.MODE_MAP.get(new_color)
    for _ in range(cycles):
        change_mode()
    config.set_color(new_color)
    config.set_power(True)
